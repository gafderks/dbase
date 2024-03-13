# Kubernetes Deployment Readme

## Deployment to Kubernetes on TransIP

1. [Install `kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl)
2. Deploy the application.  
`kubectl apply -f deployment`
3. [Configure an Nginx Ingress Controller](https://www.transip.nl/knowledgebase/artikel/7207-nginx-ingress-controller-configureren-kubernetes/)
4. [Install Cert-manager](https://www.transip.nl/knowledgebase/artikel/7042-cert-manager-installeren-op-je-kubernetes-cluster/)

## Deployment resource use

| Name                     |  CPU | Memory |
|--------------------------|-----:|-------:|
| database                 |  50m |    30M |
| nginx                    |  20m |    50M |
| web                      | 100m |   200M |
| web-init                 |   5m |     5M |
| memcached                |  20m |    70M |
| ingress-nginx-controller | 100m |    90M |
| metrics-server           | 100m |   200M |
| **Total**                | 395m |   645M |

## Backing up uploaded files

1. Retrieve the name of the pod running nginx:
```bash
kubectl get pod -l io.kompose.service=nginx --field-selector=status.phase==Running -o jsonpath="{.items[0].metadata.name}"
```
2. Copy the `/opt/services/dbase/media` folder to your local machine.
In the command below replace `nginx-6479f47879-2kvd5` with the output of the previous step. `./media-backup` is the local folder where the files will be copied.
```bash
kubectl cp nginx-6479f47879-2kvd5:/opt/services/dbase/media ./media-backup
```

## Backing up Postgres Database files

1. Retrieve the name of the pod running the database:
```bash
kubectl get pod -l io.kompose.service=database --field-selector=status.phase==Running -o jsonpath="{.items[0].metadata.name}"
```
2. Copy the `/var/lib/postgresql/data` folder to your local machine.
In the command below replace `database-7bc78f4bb9-d5z9s` with the output of the previous step. `./database-backup` is the local folder where the files will be copied.
```bash
kubectl cp database-7bc78f4bb9-d5z9s:/var/lib/postgresql/data ./database-backup
```
