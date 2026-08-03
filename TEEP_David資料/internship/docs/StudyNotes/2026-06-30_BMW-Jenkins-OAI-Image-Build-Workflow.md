---
title: BMW Jenkins Workflow for Building and Publishing OAI gNB Images
---

# BMW Jenkins Workflow for Building and Publishing OAI gNB Images

---

## 1. Why This Workflow Matters

The WINLAB / Pegatron O-RU experiment depends on a repeatable path from code change to deployed gNB:

1. Modify or select the target OAI branch.
2. Build the OAI gNB image with the correct FHI 7.2 Dockerfiles.
3. Push the image to the BMW registry.
4. Deploy that image on the lab server through Helm.
5. Change OAI runtime configuration and compare behavior against WINLAB power/throughput results.

This note covers steps 1-3. The deployment and OAI configuration side is documented separately in [2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md](./2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md).

---

## 2. Access Prerequisite: WireGuard VPN

The BMW internal sites are reachable only after connecting to the lab VPN.

Create or obtain a WireGuard config from the lab administrator. Store it outside the git repository, for example:

```bash
~/Downloads/David_TEEP.conf
```

The config has this general shape:

```ini
[Interface]
PrivateKey = <redacted-private-key>
Address = 10.1.0.106/32
DNS = 192.168.8.72
MTU = 1420

[Peer]
PublicKey = <lab-wireguard-public-key>
AllowedIPs = 10.1.0.0/24, 192.168.8.0/24, 192.168.10.0/24
Endpoint = <vpn-endpoint>:<port>
PersistentKeepalive = 25
```

Bring the tunnel up:

```bash
sudo wg-quick up ~/Downloads/David_TEEP.conf
```

Basic checks:

```bash
ip addr show
wg show
ping -c 3 192.168.8.72
```

Expected result:

- A WireGuard interface is up.
- The lab DNS server `192.168.8.72` is reachable.
- BMW internal web services resolve and load.

To shut the VPN down:

```bash
sudo wg-quick down ~/Downloads/David_TEEP.conf
```

---

## 3. Internal Sites Used by This Workflow

After the VPN is active, two main sites are required:

| Site | Purpose |
|---|---|
| `https://bmw.ece.ntust.edu.tw/` | BMW account and registry identity |
| `https://jenkins.bmw.lab/` | CI pipeline for cloning, building, and pushing OAI images |

The BMW site is the identity side. The Jenkins site is the build side. The same BMW account credentials are later referenced from Jenkins as a credential entry.

---

## 4. BMW Account Setup

1. Open `https://bmw.ece.ntust.edu.tw/`.
2. Sign in or create the required user account.
3. Record the username only in project notes.
4. Store the password in a password manager, not in git.

Screenshot from the raw note:

![BMW account page](https://hackmd.io/_uploads/H1Xk8se7Gl.png)

The username/password from this site will be used as the registry credential in Jenkins.

---

## 5. Jenkins Account Setup

Open:

```text
https://jenkins.bmw.lab/
```

Sign up or sign in, then go to the Jenkins dashboard.

![Jenkins dashboard](https://hackmd.io/_uploads/ByfBdslQzx.png)

The dashboard has cluster or project tabs across the top. In the raw example, the relevant tab was:

```text
nFAPI
```

The example job used as a reference was:

```text
ming-nfapi-Fronthaul72-e2e
```

![nFAPI dashboard example](https://hackmd.io/_uploads/rkoX_oeQMe.png)

---

## 6. Add Jenkins Credentials for the BMW Registry

Jenkins needs credentials so the pipeline can push the built image to the BMW registry.

Navigation:

1. Click the avatar icon in the top right.
2. Open **Credentials**.

![Jenkins credentials menu](https://hackmd.io/_uploads/H1zVYjx7zl.png)

3. Open the relevant domain, for example `System` -> `Global credentials`.
4. Click **Add Credentials**.

![Jenkins credential domain](https://hackmd.io/_uploads/ryPiYjl7Me.png)

Credential values:

| Field | Value |
|---|---|
| Kind | `Username with password` |
| Username | BMW account username |
| Password | BMW account password |
| ID | Prefer the same as the BMW username, unless the lab naming convention says otherwise |
| Description | Optional, for example `BMW registry credential for <username>` |

![Jenkins add credential form](https://hackmd.io/_uploads/HkOntilQGx.png)

This credential ID is later passed to the pipeline as:

```text
REGISTRY_CREDENTIAL_ID
```

---

## 7. Create a Jenkins Pipeline Item

From the Jenkins home page:

1. Click **Add item** in the top left.
2. Choose **Pipeline**.
3. Use a clear job name, for example:

```text
<username>-oai-gnb-fhi72-build
```

![Add Jenkins item](https://hackmd.io/_uploads/rJnicog7Gx.png)

If the lab already has a known-good reference job, copy from it:

```text
ming-nfapi-Fronthaul72-e2e
```

![Pipeline type and copy-from field](https://hackmd.io/_uploads/SJtkjixQzl.png)

After creating the job, Jenkins opens the pipeline configuration page. Most fields can remain default for the first build. The important field is the pipeline script.

![Jenkins pipeline script area](https://hackmd.io/_uploads/Bkp4soemGe.png)

---

## 8. Pipeline Script

The raw note provided a working Jenkinsfile-style pipeline. The professional version below keeps the same logic while making the user-specific fields explicit.

```groovy
pipeline {
    agent {
        label 'jenkins-agent-01'
    }

    environment {
        GIT_SSL_NO_VERIFY = 'true'
    }

    parameters {
        string(name: 'GIT_REPO',
               defaultValue: 'https://github.com/bmw-ece-ntust/openairinterface5g',
               description: 'Git repository URL')

        string(name: 'GIT_BRANCH',
               defaultValue: 'nfapi-DelayManagement-BMW',
               description: 'Git branch to clone')

        string(name: 'GIT_CREDENTIAL_ID',
               defaultValue: 'ming_gh_token',
               description: 'Git credentials ID. Leave empty for public repos.')

        string(name: 'QUAY_REPO',
               defaultValue: 'bmw.ece.ntust.edu.tw/<username>',
               description: 'Container registry namespace')

        string(name: 'TAG',
               defaultValue: 'latest',
               description: 'Image tag')

        string(name: 'REGISTRY_CREDENTIAL_ID',
               defaultValue: '<username>',
               description: 'Jenkins credential ID for the BMW registry')
    }

    stages {
        stage('Clone Repository') {
            options {
                timeout(time: 45, unit: 'MINUTES')
            }
            steps {
                script {
                    def gitExtensions = [
                        [$class: 'CloneOption', depth: 1, noTags: true, shallow: true, timeout: 30],
                        [$class: 'CleanBeforeCheckout']
                    ]

                    if (params.GIT_CREDENTIAL_ID?.trim()) {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "*/${params.GIT_BRANCH}"]],
                            extensions: gitExtensions,
                            userRemoteConfigs: [[
                                credentialsId: "${params.GIT_CREDENTIAL_ID}",
                                url: "${params.GIT_REPO}"
                            ]]
                        ])
                    } else {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "*/${params.GIT_BRANCH}"]],
                            extensions: gitExtensions,
                            userRemoteConfigs: [[
                                url: "${params.GIT_REPO}"
                            ]]
                        ])
                    }

                    sh 'git submodule sync --recursive'
                    sh 'git submodule update --init --recursive --force'
                    sh 'git submodule foreach --recursive git clean -xfd'
                    sh 'git submodule foreach --recursive git reset --hard'
                }
            }
        }

        stage('Build Base Image') {
            steps {
                sh 'podman build --tls-verify=false -t ran-base -f docker/Dockerfile.base.ubuntu .'
            }
        }

        stage('Build Build Image') {
            steps {
                sh 'podman build --tls-verify=false -t ran-build-fhi72 -f docker/Dockerfile.build.fhi72.ubuntu .'
            }
        }

        stage('Build gNB Image') {
            steps {
                sh 'podman build --tls-verify=false -t oai-gnb -f docker/Dockerfile.gNB.fhi72.ubuntu .'
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: params.REGISTRY_CREDENTIAL_ID,
                    usernameVariable: 'QUAY_USER',
                    passwordVariable: 'QUAY_PASS'
                )]) {
                    sh """
                        echo "${QUAY_PASS}" | podman login ${params.QUAY_REPO} --username ${QUAY_USER} --password-stdin --tls-verify=false

                        podman tag oai-gnb ${params.QUAY_REPO}/oai-gnb:${params.TAG}
                        podman push --tls-verify=false ${params.QUAY_REPO}/oai-gnb:${params.TAG}
                    """
                }
            }
        }
    }
}
```

---

## 9. Important Parameters to Change

Before the first build, update these values:

| Parameter | Meaning | Example |
|---|---|---|
| `GIT_REPO` | OAI source repository | `https://github.com/bmw-ece-ntust/openairinterface5g` |
| `GIT_BRANCH` | Branch containing the OAI code to build | `nfapi-DelayManagement-BMW` |
| `GIT_CREDENTIAL_ID` | Jenkins credential for private Git access | `ming_gh_token`, or your own token ID |
| `QUAY_REPO` | Registry namespace where the image will be pushed | `bmw.ece.ntust.edu.tw/<username>` |
| `TAG` | Image tag for deployment tracking | `latest`, `winlab-baseline-YYYYMMDD`, or a commit-derived tag |
| `REGISTRY_CREDENTIAL_ID` | Jenkins credential ID for registry login | `<username>` |

For reproducible experiments, avoid always deploying `latest`. Use explicit tags:

```text
winlab-oai-original-20260630
winlab-oai-tdm-cap27-20260630
winlab-oai-fdm-baseline-20260630
```

This makes the image used for each power run traceable.

---

## 10. What Image Is Produced?

The pipeline builds three local images inside the Jenkins agent:

| Stage | Local image name | Dockerfile |
|---|---|---|
| Build Base Image | `ran-base` | `docker/Dockerfile.base.ubuntu` |
| Build Build Image | `ran-build-fhi72` | `docker/Dockerfile.build.fhi72.ubuntu` |
| Build gNB Image | `oai-gnb` | `docker/Dockerfile.gNB.fhi72.ubuntu` |

Only the final gNB image is pushed:

```text
${QUAY_REPO}/oai-gnb:${TAG}
```

For example:

```text
bmw.ece.ntust.edu.tw/<username>/oai-gnb:winlab-oai-original-20260630
```

This is the image reference that the Helm chart must use later. Jenkins does not deploy the image by itself in this workflow; it only builds and publishes it.

Build screen from the raw note:

![Jenkins build page](https://hackmd.io/_uploads/B1xbehseXzl.png)

---

## 11. Build Verification Checklist

Before handing the image to the deployment workflow, verify:

| Check | Expected Evidence |
|---|---|
| VPN is active | `wg show` lists the active peer and latest handshake |
| Jenkins job can clone repo | `Clone Repository` stage passes |
| Submodules are initialized | No fatal errors during `git submodule update --init --recursive --force` |
| Base/build/gNB images build | All three Podman build stages pass |
| Registry login succeeds | `podman login` exits successfully |
| Image push succeeds | Jenkins log shows `podman push` completed |
| Image is traceable | Final image reference is recorded in the experiment note or run summary |

Minimum artifact to record for each experiment:

```text
GIT_REPO=
GIT_BRANCH=
OAI_COMMIT=
QUAY_REPO=
TAG=
FULL_IMAGE_REF=
JENKINS_BUILD_URL=
```

---

## 12. Common Failure Modes

| Symptom | Likely Cause | Fix |
|---|---|---|
| BMW/Jenkins pages do not load | VPN not active, DNS not using lab resolver, or route missing | Run `wg show`, check `resolvectl`, and ping `192.168.8.72` |
| Git clone fails | Private repo token missing or wrong `GIT_CREDENTIAL_ID` | Add/verify Jenkins Git credential |
| Submodule update fails | Token lacks access to submodule repos | Use a credential with recursive repo access |
| Podman build fails on missing files | Wrong branch or Dockerfile path changed | Confirm branch and Dockerfile names |
| Registry login fails | Wrong `REGISTRY_CREDENTIAL_ID` or BMW password changed | Update Jenkins credential |
| Helm deploy later pulls old code | Reused `latest` tag or chart points to old image | Use unique image tags and update Helm values |

---

## 13. Connection to WINLAB Replication

The Jenkins image workflow becomes scientifically important when scheduler or OAI config changes are compared:

| Experiment Mode | Code/Image Requirement |
|---|---|
| `oai_original` | Baseline branch/image with no scheduler modification |
| `oai_time_domain` | Branch/image with verified scheduler behavior for time-domain allocation |
| `oai_frequency_domain` | Branch/image or config that preserves/widens same-slot frequency-domain allocation |
| `oai_prb_cap_27` | Diagnostic image with `pf_dl()` grant-size cap, if implemented in OAI source |

Each power measurement run should record both:

- the image reference, proving which code was deployed;
- the OAI runtime configuration, proving which radio/TDD/cell settings were active.

---

## 14. Next Step

After the image is pushed, continue with:

[HPE OAI Helm and WINLAB Configuration Guide](./2026-06-30_HPE-OAI-Helm-and-WINLAB-Config-Guide.md)

That note explains how the HPE server, Helm chart, `values.yaml`, and OAI `configmap.yaml` connect the Jenkins-built image to the actual gNB runtime configuration.
