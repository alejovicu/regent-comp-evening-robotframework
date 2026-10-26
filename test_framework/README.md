# Robot Framework tests for the Demo Shop

## Run locally

```bash
python -m venv .venv_rf && . .venv_rf/bin/activate
pip install -r requirements.txt
robot --outputdir results features                          # visible Chrome, for debugging
BROWSER=headlesschrome robot --outputdir results features   # no window
```

Settings (`BASE_URL`, `BROWSER`, `REMOTE_URL`, `TIMEOUT`, credentials) are in `config/config.py`
and can be overridden with environment variables.

## Run in the kind cluster

`k8s/` is a Job that runs the suite in the `shopcart` namespace against `svc/frontend`, with
headless Chromium in a Selenium sidecar (`REMOTE_URL=http://localhost:4444`). The pod downloads
the test code from GitHub at `GIT_REVISION` (default `main`), so it needs no image build.

```bash
kubectl apply -k k8s
kubectl -n shopcart logs -f job/robot-tests -c robot
kubectl -n shopcart delete -k k8s     # before running it again
```

The Job fails when a test fails.

> The kind node needs memory for the app, Chromium and ArgoCD: give the Podman machine at least
> 6 GiB (Podman Desktop → Settings → Resources), the default 2 GiB is not enough.

## Run on every pull request with ArgoCD

```bash
./scripts/install-argocd.sh
```

This installs ArgoCD and `argocd/applicationset.yaml`, an ApplicationSet with a GitHub pull
request generator. It polls GitHub every 2 minutes and creates one Application per open PR
(`robot-tests-pr-<number>`) that deploys `k8s/` at the PR's head commit. Every new commit gets a
new Job named `robot-tests-pr-<number>-<sha>`, so the suite runs again on each push. Closing
the PR deletes its Application and Job.

The result shows as the Application's health: **Healthy** when all tests passed, **Degraded**
when the Job failed. Logs: `kubectl -n shopcart logs job/robot-tests-pr-<number>-<sha> -c robot`
or the pod's logs in the ArgoCD UI.

Notes:
- Unauthenticated, GitHub allows 60 API requests per hour; see the `tokenRef` comment in
  `argocd/applicationset.yaml` to use a token.
- All runs share the same app and reset its data, so runs for two PRs at the same time can
  interfere with each other.
- The tests run the PR's test code against the app currently deployed in `shopcart`;
  app changes in the PR are not built or deployed.
