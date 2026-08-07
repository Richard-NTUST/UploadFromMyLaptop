(function () {
  "use strict";

  const run = window.WINLAB_RUN_DATA;
  if (!run) {
    document.body.innerHTML = "<p>Scheduler playback data is unavailable.</p>";
    return;
  }

  const meta = run.meta;
  const schedulerEnd = meta.coverageSeconds;
  const totalTimeline = meta.trafficDurationSeconds;

  const elements = {
    play: document.getElementById("play-button"),
    reset: document.getElementById("reset-button"),
    slider: document.getElementById("time-slider"),
    elapsed: document.getElementById("elapsed-value"),
    coverage: document.getElementById("coverage-value"),
    rnti: document.getElementById("rnti-value"),
    layers: document.getElementById("layers-value"),
    grantState: document.getElementById("grant-state"),
    slot: document.getElementById("slot-value"),
    grantPrbs: document.getElementById("grant-prbs"),
    allocationFill: document.getElementById("allocation-fill"),
    allocationCap: document.getElementById("allocation-cap"),
    mcs: document.getElementById("mcs-value"),
    tbs: document.getElementById("tbs-value"),
    harq: document.getElementById("harq-value"),
    symbols: document.getElementById("symbols-value"),
    throughput: document.getElementById("throughput-value"),
    power: document.getElementById("power-value"),
    grantCount: document.getElementById("grant-count-value"),
    meanPrbs: document.getElementById("mean-prbs-value"),
    retxRate: document.getElementById("retx-rate-value"),
    eventCount: document.getElementById("event-count-value"),
    completion: document.getElementById("completion-value"),
    schedulerDuration: document.getElementById("scheduler-duration-note"),
    trafficDuration: document.getElementById("traffic-duration-note"),
    requestedDuration: document.getElementById("requested-duration-note"),
    dominantGrant: document.getElementById("dominant-grant-note"),
    grid: document.getElementById("resource-grid"),
    timeline: document.getElementById("timeline-chart")
  };

  let currentTime = 0;
  let speed = 1;
  let playing = false;
  let previousFrame = performance.now();

  elements.slider.max = String(schedulerEnd);
  elements.rnti.textContent = "0x" + meta.rnti;
  elements.coverage.textContent = "00:00-" + formatClock(schedulerEnd, true) + " relative time";
  elements.eventCount.textContent = formatNumber(meta.eventCount) + " grants";
  elements.completion.textContent = meta.completionPercent.toFixed(1) + "% complete";
  elements.schedulerDuration.textContent = formatClock(schedulerEnd, true);
  elements.trafficDuration.textContent = formatClock(meta.trafficDurationSeconds);
  elements.requestedDuration.textContent = formatClock(meta.requestedDurationSeconds);
  elements.dominantGrant.textContent =
    meta.dominantGrantPercent.toFixed(1) + "% of grants at " +
    meta.dominantGrantPrbs + " PRBs";

  function formatClock(seconds, tenths) {
    const safe = Math.max(0, seconds || 0);
    const minutes = Math.floor(safe / 60);
    const remaining = safe - minutes * 60;
    if (tenths) {
      return String(minutes).padStart(2, "0") + ":" + remaining.toFixed(1).padStart(4, "0");
    }
    return String(minutes).padStart(2, "0") + ":" + String(Math.floor(remaining)).padStart(2, "0");
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("en-US").format(value);
  }

  function sampleStep(series, time, field) {
    if (!series.length) return 0;
    const index = Math.max(0, Math.min(series.length - 1, Math.floor(time)));
    return series[index][field] || 0;
  }

  function sampleLinear(series, time, field) {
    if (!series.length) return 0;
    if (time <= series[0].t) return series[0][field];
    if (time >= series[series.length - 1].t) return series[series.length - 1][field];
    let low = 0;
    let high = series.length - 1;
    while (low + 1 < high) {
      const middle = Math.floor((low + high) / 2);
      if (series[middle].t <= time) low = middle;
      else high = middle;
    }
    const left = series[low];
    const right = series[high];
    const ratio = (time - left.t) / Math.max(0.001, right.t - left.t);
    return left[field] + (right[field] - left[field]) * ratio;
  }

  function currentBucket() {
    const index = Math.max(0, Math.min(run.scheduler.length - 1, Math.floor(currentTime)));
    return run.scheduler[index];
  }

  function visibleEvents() {
    const bucketIndex = Math.floor(currentTime);
    const events = [];
    for (let index = Math.max(0, bucketIndex - 3); index <= bucketIndex; index += 1) {
      const bucket = run.scheduler[index];
      if (!bucket) continue;
      for (const event of bucket.events) {
        if (event.t <= currentTime + 0.001) events.push(event);
      }
    }
    return events.slice(-12);
  }

  function activeEvent(events) {
    if (!events.length) return null;
    return events[events.length - 1];
  }

  function updateMetrics() {
    const bucket = currentBucket();
    const events = visibleEvents();
    const grant = activeEvent(events);
    const throughput = meta.meanThroughputMbps;
    const power = meta.meanPowerWatts;

    elements.elapsed.textContent = formatClock(currentTime, true);
    elements.slider.value = String(currentTime);
    elements.throughput.textContent = throughput.toFixed(1);
    elements.power.textContent = power.toFixed(2);
    elements.grantCount.textContent = String(bucket.grantCount);
    elements.meanPrbs.textContent = bucket.meanPrbs.toFixed(1);
    elements.retxRate.textContent = bucket.retxRate.toFixed(1);

    if (!grant) {
      elements.grantState.textContent = "No logged grant";
      elements.slot.textContent = "Frame -- / slot --";
      elements.grantPrbs.textContent = "0";
      elements.layers.textContent = "-";
      elements.mcs.textContent = "-";
      elements.tbs.textContent = "-";
      elements.harq.textContent = "-";
      elements.symbols.textContent = "-";
      elements.allocationFill.style.width = "0";
      return;
    }

    elements.grantState.textContent = grant.retx ? "HARQ retransmission" : "New transmission";
    elements.slot.textContent = "Frame " + grant.frame + " / slot " + grant.slot;
    elements.grantPrbs.textContent = String(grant.rbSize);
    elements.layers.textContent = String(grant.layers);
    elements.mcs.textContent = String(grant.mcs);
    elements.tbs.textContent = formatNumber(grant.tbs) + " B";
    elements.harq.textContent = String(grant.harq);
    elements.symbols.textContent = grant.symStart + ":" + grant.symCount;

    const experimentCap = meta.maxNewTxPrbs;
    const width = Math.min(100, 100 * grant.rbSize / experimentCap);
    elements.allocationFill.style.width = width + "%";
    elements.allocationFill.style.marginLeft = "0";
    elements.allocationFill.style.backgroundColor = grant.retx ? "#f39145" : "#4ea1ff";
  }

  function prepareCanvas(canvas) {
    const rect = canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    const width = Math.max(1, Math.round(rect.width * ratio));
    const height = Math.max(1, Math.round(rect.height * ratio));
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { context, width: rect.width, height: rect.height };
  }

  function drawResourceGrid() {
    const { context, width, height } = prepareCanvas(elements.grid);
    const bucketIndex = Math.floor(currentTime);
    const windowSeconds = 30;
    const firstBucket = Math.max(0, bucketIndex - windowSeconds + 1);
    const buckets = run.scheduler.slice(firstBucket, bucketIndex + 1);
    const left = 42;
    const right = 14;
    const top = 18;
    const bottom = 34;
    const plotWidth = width - left - right;
    const plotHeight = height - top - bottom;
    const cap = meta.maxNewTxPrbs;

    context.clearRect(0, 0, width, height);
    context.fillStyle = "#0a120f";
    context.fillRect(left, top, plotWidth, plotHeight);

    context.strokeStyle = "#28352e";
    context.lineWidth = 1;
    [0, 5, 10, 15, 20, 25, cap].forEach((prbs) => {
      const y = top + plotHeight * (1 - prbs / cap);
      context.beginPath();
      context.moveTo(left, y);
      context.lineTo(left + plotWidth, y);
      context.stroke();
      context.fillStyle = "#8f978f";
      context.font = "10px ui-monospace, monospace";
      context.textAlign = "right";
      context.fillText(String(prbs), left - 7, y + 3);
    });

    if (!buckets.length) return;
    const step = plotWidth / windowSeconds;
    const startOffset = windowSeconds - buckets.length;

    buckets.forEach((bucket, index) => {
      const x = left + (startOffset + index) * step;
      const meanHeight = plotHeight * bucket.meanPrbs / cap;
      context.fillStyle = bucket.retxRate > 0 ? "#f39145" : "#4fc8c5";
      context.fillRect(x + 1, top + plotHeight - meanHeight, Math.max(2, step - 2), meanHeight);
    });

    context.strokeStyle = "#a8dc68";
    context.lineWidth = 2;
    context.beginPath();
    buckets.forEach((bucket, index) => {
      const x = left + (startOffset + index + 0.5) * step;
      const y = top + plotHeight * (1 - bucket.maxPrbs / cap);
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.stroke();

    context.fillStyle = "#8f978f";
    context.font = "10px ui-monospace, monospace";
    context.textAlign = "left";
    context.fillText("-" + (buckets.length - 1) + "s", left, height - 10);
    context.textAlign = "right";
    context.fillText("now", left + plotWidth, height - 10);
  }

  function drawTimeline() {
    const { context, width, height } = prepareCanvas(elements.timeline);
    const left = 46;
    const right = 42;
    const top = 16;
    const bottom = 34;
    const plotWidth = width - left - right;
    const plotHeight = height - top - bottom;
    const throughputMax = Math.max(meta.offeredLoadMbps, 200);
    const powerValues = run.power.map((sample) => sample.watts);
    const powerMin = Math.floor(Math.min.apply(null, powerValues) - 1);
    const powerMax = Math.ceil(Math.max.apply(null, powerValues) + 1);

    context.clearRect(0, 0, width, height);
    context.fillStyle = "#0a120f";
    context.fillRect(left, top, plotWidth, plotHeight);

    context.strokeStyle = "#28352e";
    context.lineWidth = 1;
    context.font = "10px ui-monospace, monospace";
    context.fillStyle = "#8f978f";
    for (let line = 0; line <= 4; line += 1) {
      const y = top + plotHeight * line / 4;
      context.beginPath();
      context.moveTo(left, y);
      context.lineTo(left + plotWidth, y);
      context.stroke();
      context.textAlign = "right";
      context.fillText(String(Math.round(throughputMax * (1 - line / 4))), left - 7, y + 3);
    }

    context.beginPath();
    run.throughput.forEach((sample, index) => {
      const x = left + plotWidth * sample.t / totalTimeline;
      const y = top + plotHeight * (1 - sample.mbps / throughputMax);
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.strokeStyle = "#43c7c3";
    context.lineWidth = 2;
    context.stroke();

    context.beginPath();
    run.power.forEach((sample, index) => {
      const x = left + plotWidth * sample.t / totalTimeline;
      const y = top + plotHeight * (1 - (sample.watts - powerMin) / (powerMax - powerMin));
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.strokeStyle = "#f39145";
    context.lineWidth = 2;
    context.stroke();

    context.fillStyle = "#8f978f";
    context.textAlign = "left";
    context.fillText(powerMax + " W", width - right + 6, top + 3);
    context.fillText(powerMin + " W", width - right + 6, top + plotHeight);

    for (let minute = 0; minute <= Math.floor(totalTimeline / 300); minute += 1) {
      const seconds = minute * 300;
      const x = left + plotWidth * seconds / totalTimeline;
      context.textAlign = "center";
      context.fillText(formatClock(seconds), x, height - 10);
    }

  }

  function render() {
    updateMetrics();
    drawResourceGrid();
    drawTimeline();
  }

  function setPlaying(next) {
    playing = next;
    elements.play.textContent = playing ? "Pause" : "Play";
    elements.play.setAttribute("aria-label", playing ? "Pause scheduler playback" : "Play scheduler playback");
    previousFrame = performance.now();
  }

  function tick(timestamp) {
    const delta = Math.min(0.1, (timestamp - previousFrame) / 1000);
    previousFrame = timestamp;
    if (playing) {
      currentTime += delta * speed;
      if (currentTime >= schedulerEnd) {
        currentTime = schedulerEnd;
        setPlaying(false);
      }
      render();
    }
    requestAnimationFrame(tick);
  }

  elements.play.addEventListener("click", function () {
    if (!playing && currentTime >= schedulerEnd) currentTime = 0;
    setPlaying(!playing);
    render();
  });

  elements.reset.addEventListener("click", function () {
    currentTime = 0;
    setPlaying(false);
    render();
  });

  elements.slider.addEventListener("input", function () {
    currentTime = Number(elements.slider.value);
    setPlaying(false);
    render();
  });

  document.querySelectorAll("[data-speed]").forEach(function (button) {
    button.addEventListener("click", function () {
      speed = Number(button.dataset.speed);
      document.querySelectorAll("[data-speed]").forEach(function (candidate) {
        candidate.classList.toggle("active", candidate === button);
      });
    });
  });

  window.addEventListener("resize", render);
  render();
  requestAnimationFrame(tick);
}());
