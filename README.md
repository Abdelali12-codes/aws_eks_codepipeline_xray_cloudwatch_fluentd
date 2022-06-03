# aws_eks_cluster

## create eks cluster using the config file

```
eksctl create cluster -f cluster.yaml
```
## delete eks cluster


```
kubectl get svc --all-namespaces
kubectl delete svc <service-name>
eksctl delete cluster --name <prod>

```

## create ebs csi driver 

* be sure that once you create your cluster you have enabled OIDC, otherwise the next steps 
will not work for you

* create policy that you want to attach to your csi driver pod
* create a role and attach it to the serviceaccount that will be mounted to the pod to allow it make apicalls 
on your behalf



* run the below command to create the role, attach the policies to it and attach that role to serviceaccount

```
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster my-cluster \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve \
  --role-only \
  --role-name AmazonEKS_EBS_CSI_DriverRole \ (this is the role will be created)
  --override-existing-serviceaccounts 
    
```

* to allow the csi driver to encrypt your ebs volumes, add it the permission to achieve that

1. create file and paste the below content to it

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant"
      ],
      "Resource": ["custom-key-id"],
      "Condition": {
        "Bool": {
          "kms:GrantIsForAWSResource": "true"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": ["custom-key-id"]
    }
  ]
}
```
change the custom-key-id with the one you have on your account (customer key)

2. create a policy from the above file

```
aws iam create-policy \
  --policy-name KMS_Key_For_Encryption_On_EBS_Policy \
  --policy-document file://kms-key-for-encryption-on-ebs.json

```
3. attach the policy to the role you have attached to service account on the above lines
```
aws iam attach-role-policy \
  --policy-arn arn:aws:iam::111122223333:policy/KMS_Key_For_Encryption_On_EBS_Policy \
  --role-name AmazonEKS_EBS_CSI_DriverRole
```

4. create oidc for an existing cluster

* Determine whether you have an existing IAM OIDC provider for your cluster

```
aws eks describe-cluster --name my-cluster --query "cluster.identity.oidc.issuer" --output text
```

* List the IAM OIDC providers in your account

```
aws iam list-open-id-connect-providers
```

* Create an IAM OIDC identity provider for your cluster with the following command

```
eksctl utils associate-iam-oidc-provider --cluster my-cluster --approve
```
# aws_eks_codepipeline_xray_cloudwatch_fluentd
