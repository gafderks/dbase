# Deployment to Kubernetes on TransIP

1. [Install `kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl)
2. Deploy the application.  
`kubectl apply -f deployment`
3. [Configure an Nginx Ingress Controller](https://www.transip.nl/knowledgebase/artikel/7207-nginx-ingress-controller-configureren-kubernetes/)
4. [Install Cert-manager](https://www.transip.nl/knowledgebase/artikel/7042-cert-manager-installeren-op-je-kubernetes-cluster/)

# Deployment resource use

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
