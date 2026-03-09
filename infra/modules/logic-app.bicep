@description('Azure region')
param location string

@description('Azure DevOps organization name')
param adoOrganization string

@description('Azure DevOps project name')
param adoProject string

@secure()
@description('Azure DevOps PAT')
param adoPat string

@secure()
@description('GitHub PAT')
param githubPat string

@secure()
@description('Webhook secret for HMAC validation')
param webhookSecret string

@description('ADO work item type')
param workItemType string = 'Issue'

var logicAppName = 'ghas-ado-sync-${uniqueString(resourceGroup().id)}'
var workflowDefinition = loadJsonContent('../workflows/ghas-to-ado.json')

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppName
  location: location
  tags: {
    purpose: 'GHAS-ADO-Sync'
    managedBy: 'Bicep'
  }
  properties: {
    state: 'Enabled'
    definition: workflowDefinition
    parameters: {
      adoOrganization: {
        value: adoOrganization
      }
      adoProject: {
        value: adoProject
      }
      adoPat: {
        value: adoPat
      }
      githubPat: {
        value: githubPat
      }
      webhookSecret: {
        value: webhookSecret
      }
      workItemType: {
        value: workItemType
      }
    }
  }
}

output triggerUrl string = listCallbackUrl('${logicApp.id}/triggers/When_a_GHAS_webhook_is_received', '2019-05-01').value
output logicAppName string = logicApp.name
output logicAppResourceId string = logicApp.id
