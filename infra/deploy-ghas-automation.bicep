targetScope = 'resourceGroup'

// Entry point: GitHub Advanced Security (GHAS) -> Azure Boards work item automation.
// A GitHub webhook (repo / org / enterprise level) posts secret-scanning, code-scanning,
// and Dependabot alerts to the Logic App, which creates and auto-closes work items in
// Azure Boards. Mirrors deploy-full-automation.bicep (the ADO-sourced GHAzDO flow).

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Azure DevOps organization name (e.g. "myorg" from https://dev.azure.com/myorg)')
param adoOrganization string

@description('Azure DevOps project name that owns the Azure Boards work items')
param adoProject string

@secure()
@description('Azure DevOps PAT with "Work Items: Read & Write" scope')
param adoPat string

@secure()
@description('Optional GitHub PAT. Not required for the webhook-driven flow; reserved for future API enrichment.')
param githubPat string = ''

@secure()
@description('Optional secret shared with the GitHub webhook. The trigger URL is SAS-signed; HMAC enforcement is a future enhancement.')
param webhookSecret string = ''

@description('ADO work item type to create (e.g. Issue, Bug, Task)')
param workItemType string = 'Issue'

@description('State to set when closing work items. Agile="Closed", Scrum="Done", Basic="Done", CMMI="Closed"')
param closedState string = 'Done'

module ghasLogicApp 'modules/logic-app.bicep' = {
  name: 'ghas-to-ado-boards-logic-app'
  params: {
    location: location
    adoOrganization: adoOrganization
    adoProject: adoProject
    adoPat: adoPat
    githubPat: githubPat
    webhookSecret: webhookSecret
    workItemType: workItemType
    closedState: closedState
  }
}

@description('Paste this into the GitHub webhook "Payload URL" (repo / org / enterprise settings).')
output webhookPayloadUrl string = ghasLogicApp.outputs.triggerUrl

output logicAppName string = ghasLogicApp.outputs.logicAppName
