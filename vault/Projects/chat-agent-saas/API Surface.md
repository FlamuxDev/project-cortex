---
cortex-generated: true
title: chat-agent-saas api
tags: [api/project]
---

# chat-agent-saas — API Surface

526 routes. Grouped by owning file; every route names its handler.

## `packages/api/src/app.ts`

- **USE** `/api/agents` → integrationRoutes
- **USE** `/api/agents` → analyticsRoutes
- **USE** `/api/agents` → actionsRoutes
- **USE** `/api/agents` → knowledgeRoutes
- **USE** `/api/agents` → agentRoutes
- **USE** `/api/agents/:agentId/channels` → channelsRoutes
- **USE** `/api/ai` → aiRoutes
- **USE** `/api/artifacts` → artifactRoutes
- **USE** `/api/auth` → authRoutes
- **USE** `/api/booking` → bookingPublicRoutes
- **USE** `/api/chat` → chatRoutes
- **USE** `/api/chat` → identityRoutes
- **USE** `/api/consent` → consentRoutes
- **GET** `/api/docs`
- **USE** `/api/dynatrace` → dynatraceRoutes
- **USE** `/api/files` → filesRoutes
- **GET** `/api/health`
- **USE** `/api/identity` → identityAdminRoutes
- **USE** `/api/integrations/catalog` → catalogRoutes
- **USE** `/api/integrations/connections` → connectionsRoutes
- **USE** `/api/integrations/oauth` → oauthRoutes
- **USE** `/api/integrations/webhook` → metaWebhookRoutes
- **USE** `/api/mcp` → mcpRoutes
- **USE** `/api/mcp/elevenlabs` → voiceMcpRoutes
- **GET** `/api/metrics` → `async`
- **USE** `/api/notifications` → notificationRoutes
- **USE** `/api/odoo` → odooRoutes
- **GET** `/api/openapi.json`
- **USE** `/api/org` → orgRoutes
- **USE** `/api/outreach` → outreachRoutes
- **USE** `/api/outreach` → outreachPublicRoutes
- **USE** `/api/outreach/email-domains` → emailDomainRoutes
- **USE** `/api/outreach/journeys` → journeyRoutes
- **USE** `/api/outreach/push` → pushRoutes
- **USE** `/api/outreach/segments` → segmentRoutes
- **USE** `/api/platform` → platformRoutes
- **USE** `/api/push` → pushPublicRoutes
- **GET** `/api/ready` → `async`
- **USE** `/api/reports` → reportRoutes
- **USE** `/api/roles` → roleRoutes
- …and 7 more

## `packages/api/src/modules/agents/actions.routes.ts`

- **POST** `/:agentId/actions` → actionsController.createAction
- **GET** `/:agentId/actions` → actionsController.listActions
- **DELETE** `/:agentId/actions/:actionId` → actionsController.deleteAction
- **PUT** `/:agentId/actions/:actionId` → actionsController.updateAction
- **POST** `/:agentId/actions/:actionId/test` → actionsController.testAction

## `packages/api/src/modules/agents/agent.routes.ts`

- **POST** `/` → agentController.createAgent
- **GET** `/` → agentController.getAgents
- **GET** `/:agentId/support/conversations/:conversationId` → supportController.getDetail
- **POST** `/:agentId/support/conversations/:conversationId/ai-brief` → supportController.postAiBrief
- **POST** `/:agentId/support/conversations/:conversationId/reply` → supportController.postReply
- **POST** `/:agentId/support/conversations/:conversationId/resolve` → supportController.postResolve
- **PUT** `/:agentId/support/conversations/:conversationId/summary` → supportController.putStaffSummary
- **GET** `/:agentId/support/metrics` → supportController.getMetrics
- **GET** `/:agentId/support/queue` → supportController.getQueue
- **DELETE** `/:id` → agentController.deleteAgent
- **PUT** `/:id` → agentController.updateAgent
- **GET** `/:id` → agentController.getAgentById
- **PUT** `/:id/config` → agentConfigController.updateAgentConfig
- **GET** `/:id/config` → agentConfigController.getAgentConfig
- **POST** `/:id/config/suggest-description` → agentConfigController.suggestDescription
- **GET** `/:id/elevenlabs/signed-url` → agentController.getElevenlabsSignedUrl
- **POST** `/:id/widget/upload-image` → agentConfigController.uploadWidgetImage

## `packages/api/src/modules/ai-studio/ai.routes.ts`

- **POST** `/campaign-studio/draft` → ai.campaignDraft
- **POST** `/content/ads` → ai.contentAds
- **POST** `/content/messages` → ai.contentMessages
- **POST** `/content/variants` → ai.contentVariants
- **POST** `/insights/:campaignId` → ai.campaignInsights
- **POST** `/predict` → ai.predictPerformance

## `packages/api/src/modules/analytics/analytics.routes.ts`

- **GET** `/:agentId/analytics/channels` → analyticsController.getChannels
- **GET** `/:agentId/analytics/overview` → analyticsController.getOverview
- **GET** `/:agentId/analytics/report` → reportController.getReport
- **GET** `/:agentId/analytics/report/export` → reportController.exportReport
- **GET** `/:agentId/analytics/sentiment` → analyticsController.getSentiment
- **GET** `/:agentId/analytics/timeline` → analyticsController.getTimeline
- **GET** `/:agentId/issues` → analyticsController.getIssues
- **POST** `/:agentId/issues/:analysisId/reopen` → analyticsController.reopenQualityAlert
- **POST** `/:agentId/issues/:analysisId/resolve` → analyticsController.resolveQualityAlert

## `packages/api/src/modules/artifacts/artifact.routes.ts`

- **GET** `/:id/download` → `async`
- **GET** `/:id/preview` → `async`
- **GET** `/:id/preview.json` → `async`

## `packages/api/src/modules/auth/auth.routes.ts`

- **POST** `/accept-invite` → authController.acceptInvite
- **POST** `/forgot-password` → authController.forgotPassword
- **GET** `/invitations/:token` → authController.getInviteDetails
- **POST** `/login` → authController.login
- **POST** `/logout` → authController.logout
- **GET** `/me` → authController.getMe
- **POST** `/refresh` → authController.refresh
- **POST** `/register` → authController.register
- **POST** `/resend-verification` → authController.resendVerification
- **POST** `/reset-password` → authController.resetPassword
- **POST** `/sign-out-all` → authController.signOutAll
- **POST** `/verify-email` → authController.verifyEmail

## `packages/api/src/modules/booking/booking.public.routes.ts`

- **POST** `/book` → bookingController.publicBook
- **GET** `/info` → bookingController.publicInfo
- **GET** `/slots` → bookingController.publicSlots

## `packages/api/src/modules/chat/chat.routes.ts`

- **GET** `/:agentId/conversations` → chatController.getConversations
- **POST** `/:agentId/conversations/:conversationId/close` → chatController.closeConversationPublic
- **GET** `/:agentId/conversations/:conversationId/export` → chatController.exportTranscriptPublic
- **POST** `/:agentId/conversations/:conversationId/handoff` → chatController.requestHandoffPublic
- **GET** `/:agentId/conversations/:conversationId/messages` → chatController.getConversationMessages
- **POST** `/:agentId/conversations/:conversationId/rating` → chatController.submitRatingPublic
- **PUT** `/:agentId/conversations/:conversationId/tags` → chatController.updateConversationTags
- **GET** `/:agentId/conversations/:conversationId/widget-messages` → chatController.getWidgetMessages
- **POST** `/:agentId/message` → chatController.processMessage
- **POST** `/:agentId/playground/conversations/:conversationId/close` → chatController.closePlaygroundConversation
- **POST** `/:agentId/playground/conversations/:conversationId/handoff` → chatController.requestPlaygroundHandoff
- **POST** `/:agentId/playground/message` → chatController.playgroundMessage
- **POST** `/:agentId/stream` → chatController.streamMessage
- **POST** `/:agentId/upload-attachment` → chatController.uploadAttachment

## `packages/api/src/modules/chat/identity.routes.ts`

- **POST** `/:agentId/identity/exchange` → `async`
- **POST** `/:agentId/identity/revoke` → `async`
- **GET** `/:agentId/identity/session` → `async`

## `packages/api/src/modules/chat/widget.routes.ts`

- **GET** `/:agentId/config` → `async`
- **GET** `/:agentId/elevenlabs/signed-url` → `async`
- **POST** `/:agentId/elevenlabs/stop` → `async`

## `packages/api/src/modules/dynatrace/dynatrace.routes.ts`

- **POST** `/agents/:agentId/connections` → dynatraceController.attachAgent
- **GET** `/agents/:agentId/connections` → dynatraceController.listAgentAttachments
- **DELETE** `/agents/:agentId/connections/:attachmentId` → dynatraceController.detachAgent
- **PUT** `/agents/:agentId/connections/:attachmentId` → dynatraceController.updateAttachment
- **POST** `/connections` → dynatraceController.createConnection
- **GET** `/connections` → dynatraceController.listConnections
- **DELETE** `/connections/:id` → dynatraceController.deleteConnection
- **PUT** `/connections/:id` → dynatraceController.updateConnection
- **GET** `/connections/:id` → dynatraceController.getConnection
- **POST** `/connections/:id/scan` → dynatraceController.scanConnection
- **POST** `/connections/:id/test` → dynatraceController.testConnection

## `packages/api/src/modules/files/files.routes.ts`

- **GET** `/:key(*)` → `async`

## `packages/api/src/modules/identity/identity.admin.routes.ts`

- **GET** `/:id` → `async`
- **POST** `/:id/purge-memory` → `async`
- **PUT** `/:id/retention` → `async`

## `packages/api/src/modules/integrations/catalog.routes.ts`

- **GET** `/` → `async`

## `packages/api/src/modules/integrations/channels.routes.ts`

- **POST** `/` → ctrl.bind
- **GET** `/` → ctrl.list
- **PATCH** `/:id` → ctrl.patch
- **DELETE** `/:id` → ctrl.unbind
- **POST** `/:id/test` → ctrl.test

## `packages/api/src/modules/integrations/connections.routes.ts`

- **GET** `/` → ctrl.list
- **DELETE** `/:id` → ctrl.remove
- **GET** `/:id` → ctrl.get
- **GET** `/:id/resources` → ctrl.resources
- **POST** `/:id/test` → ctrl.test

## `packages/api/src/modules/integrations/integration.routes.ts`

- **POST** `/:agentId/integrations` → integrationController.addIntegration
- **GET** `/:agentId/integrations` → integrationController.getIntegrations
- **DELETE** `/:agentId/integrations/:id` → integrationController.deleteIntegration
- **PUT** `/:agentId/integrations/:id` → integrationController.updateIntegration
- **POST** `/:agentId/integrations/:id/test` → integrationController.testIntegration

## `packages/api/src/modules/integrations/oauth.routes.ts`

- **GET** `/:provider/callback` → ctrl.callback
- **POST** `/:provider/start` → ctrl.start
- **POST** `/:provider/start-platform` → ctrl.startPlatform
- **POST** `/email-bridge/connect` → ctrl.connectEmailBridge
- **GET** `/meta/byoa-info` → ctrl.metaByoaInfo
- **GET** `/meta/config` → ctrl.metaConfig
- **POST** `/meta/exchange` → ctrl.metaEmbeddedSignupExchange
- **POST** `/teams/connect` → ctrl.connectTeams

## `packages/api/src/modules/integrations/webhook-meta.routes.ts`

- **POST** `/meta` → `async`
- **GET** `/meta` → `async`

## `packages/api/src/modules/integrations/webhook-v2.routes.ts`

- **POST** `/:provider/:channelId` → `async`
- **GET** `/:provider/:channelId` → `async`

## `packages/api/src/modules/integrations/webhook.routes.ts`

- **POST** `/elevenlabs/:agentId` → `async`
- **POST** `/email/:agentId` → `async`
- **POST** `/http/:agentId` → `async`
- **POST** `/telegram/:agentId` → `async`
- **POST** `/whatsapp/:agentId` → `async`
- **GET** `/whatsapp/:agentId` → `async`

## `packages/api/src/modules/knowledge/knowledge.routes.ts`

- **GET** `/:agentId/knowledge` → knowledgeController.getSources
- **DELETE** `/:agentId/knowledge/:sourceId` → knowledgeController.deleteSource
- **POST** `/:agentId/knowledge/:sourceId/resync` → knowledgeController.resyncSource
- **POST** `/:agentId/knowledge/files` → knowledgeController.uploadFiles
- **POST** `/:agentId/knowledge/resync-all` → knowledgeController.resyncAllSources
- **GET** `/:agentId/knowledge/suggestions` → suggestionsController.listSuggestions
- **POST** `/:agentId/knowledge/suggestions/:suggestionId/accept` → suggestionsController.acceptSuggestion
- **POST** `/:agentId/knowledge/suggestions/:suggestionId/dismiss` → suggestionsController.dismissSuggestion
- **POST** `/:agentId/knowledge/suggestions/import-from-conversations` → suggestionsController.importFromConversations
- **POST** `/:agentId/knowledge/urls` → knowledgeController.addUrl
- **POST** `/:agentId/knowledge/website/confirm` → knowledgeController.confirmWebsitePages
- **POST** `/:agentId/knowledge/website/discover` → knowledgeController.discoverWebsite

## `packages/api/src/modules/mcp/mcp.routes.ts`

- **POST** `/agents/:agentId/servers` → mcpController.attachAgent
- **GET** `/agents/:agentId/servers` → mcpController.listAgentAttachments
- **DELETE** `/agents/:agentId/servers/:attachmentId` → mcpController.detachAgent
- **PUT** `/agents/:agentId/servers/:attachmentId` → mcpController.updateAttachment
- **POST** `/servers` → mcpController.createServer
- **GET** `/servers` → mcpController.listServers
- **DELETE** `/servers/:id` → mcpController.deleteServer
- **PUT** `/servers/:id` → mcpController.updateServer
- **GET** `/servers/:id` → mcpController.getServer
- **POST** `/servers/:id/refresh-tools` → mcpController.refreshTools
- **POST** `/servers/:id/test` → mcpController.testServer

## `packages/api/src/modules/notifications/notification.routes.ts`

- **GET** `/` → notificationController.getNotifications
- **POST** `/:id/read` → notificationController.markRead
- **POST** `/read-all` → notificationController.markAllRead
- **GET** `/unread-count` → notificationController.getUnreadCount

## `packages/api/src/modules/odoo/odoo.routes.ts`

- **POST** `/agents/:agentId/connections` → odooController.attachAgent
- **GET** `/agents/:agentId/connections` → odooController.listAgentAttachments
- **DELETE** `/agents/:agentId/connections/:attachmentId` → odooController.detachAgent
- **PUT** `/agents/:agentId/connections/:attachmentId` → odooController.updateAttachment
- **POST** `/connections` → odooController.createConnection
- **GET** `/connections` → odooController.listConnections
- **DELETE** `/connections/:id` → odooController.deleteConnection
- **PUT** `/connections/:id` → odooController.updateConnection
- **GET** `/connections/:id` → odooController.getConnection
- **GET** `/connections/:id/activity` → odooController.connectionActivity
- **PUT** `/connections/:id/custom-models` → odooController.setCustomModelPolicy
- **GET** `/connections/:id/custom-models` → odooController.getCustomModelPolicy
- **POST** `/connections/:id/rotate-secret` → odooController.rotateAddonSecret
- **POST** `/connections/:id/scan` → odooController.scanConnection
- **POST** `/connections/:id/test` → odooController.testConnection
- **GET** `/operations` → odooController.listOperations
- **GET** `/operations/:id` → odooController.getOperation
- **POST** `/operations/:id/approve` → odooController.approveOperation
- **POST** `/operations/:id/reject` → odooController.rejectOperation

## `packages/api/src/modules/organizations/consent.routes.ts`

- **POST** `/` → gdprController.recordConsent

## `packages/api/src/modules/organizations/org.routes.ts`

- **GET** `/audit-logs` → orgController.getOrgAuditLogs
- **POST** `/gdpr/account-deletion` → gdprController.requestAccountDeletion
- **POST** `/gdpr/erase-subject` → gdprController.eraseSubject
- **GET** `/gdpr/export` → gdprController.exportData
- **POST** `/logo` → orgController.uploadLogo
- **PUT** `/profile` → orgController.updateOrganization
- **GET** `/profile` → orgController.getOrganization

## `packages/api/src/modules/outreach/emailDomain.routes.ts`

- **POST** `/` → emailDomainController.createDomain
- **GET** `/` → emailDomainController.listDomains
- **DELETE** `/:id` → emailDomainController.deleteDomain
- **GET** `/:id` → emailDomainController.getDomain
- **POST** `/:id/verify` → emailDomainController.verifyDomain

## `packages/api/src/modules/outreach/journey.routes.ts`

- **POST** `/` → journeyController.createJourney
- **GET** `/` → journeyController.listJourneys
- **DELETE** `/:id` → journeyController.deleteJourney
- **PUT** `/:id` → journeyController.updateJourney
- **GET** `/:id` → journeyController.getJourney
- **POST** `/:id/enroll` → journeyController.enrollJourney
- **GET** `/:id/stats` → journeyController.getJourneyStats
- **POST** `/:id/status` → journeyController.setJourneyStatus

## `packages/api/src/modules/outreach/outreach.public.routes.ts`

- **GET** `/t/c/:token` → `async`
- **GET** `/t/o/:recipientId` → `async`
- **GET** `/u/:token` → `async`
- **POST** `/webhooks/email/:orgId` → `async`

## `packages/api/src/modules/outreach/outreach.routes.ts`

- **POST** `/campaigns` → campaignController.createCampaign
- **GET** `/campaigns` → campaignController.listCampaigns
- **DELETE** `/campaigns/:campaignId` → campaignController.deleteCampaign
- **PATCH** `/campaigns/:campaignId` → campaignController.updateCampaign
- **GET** `/campaigns/:campaignId` → campaignController.getCampaign
- **POST** `/campaigns/:campaignId/approve` → campaignController.approveCampaign
- **POST** `/campaigns/:campaignId/pause` → campaignController.pauseCampaign
- **POST** `/campaigns/:campaignId/prepare` → campaignController.prepareCampaign
- **GET** `/campaigns/:campaignId/recipients` → campaignController.getRecipients
- **PATCH** `/campaigns/:campaignId/recipients/:recipientId` → campaignController.updateRecipient
- **GET** `/campaigns/:campaignId/results` → campaignController.getCampaignResults
- **POST** `/campaigns/:campaignId/send` → campaignController.startCampaign
- **GET** `/channel-health` → `async`
- **POST** `/channel-health/:id/resume` → `async`
- **POST** `/lists` → outreachController.uploadList
- **GET** `/lists` → outreachController.listLists
- **DELETE** `/lists/:listId` → outreachController.deleteList
- **GET** `/lists/:listId` → outreachController.getList
- **POST** `/lists/:listId/contacts` → outreachController.addContact
- **GET** `/lists/:listId/contacts` → outreachController.getContacts
- **PATCH** `/lists/:listId/contacts/:contactId` → outreachController.updateContact
- **POST** `/lists/:listId/reimport` → outreachController.reimportList
- **POST** `/lists/:listId/segment` → outreachController.segmentList
- **POST** `/lists/manual` → outreachController.createManualList
- **GET** `/suppressions` → `async`
- **DELETE** `/suppressions/:id` → `async`

## `packages/api/src/modules/outreach/segment.routes.ts`

- **POST** `/` → segmentController.createSegment
- **GET** `/` → segmentController.listSegments
- **DELETE** `/:id` → segmentController.deleteSegment
- **PUT** `/:id` → segmentController.updateSegment
- **GET** `/:id` → segmentController.getSegment
- **POST** `/:id/rebuild` → segmentController.rebuildSegment
- **POST** `/preview` → segmentController.previewSegment

## `packages/api/src/modules/platform/platform-billing.service.ts`

- **GET** `elevenlabs-convai`

## `packages/api/src/modules/platform/platform.routes.ts`

- **POST** `/admins` → platformAdminsController.createAdmin
- **GET** `/admins` → platformAdminsController.listAdmins
- **PATCH** `/admins/:id` → platformAdminsController.patchAdmin
- **POST** `/admins/:id/password` → platformAdminsController.setPassword
- **GET** `/agents` → platformAgentsController.listAllAgents
- **DELETE** `/agents/:agentId` → platformAgentsController.adminDeleteAgent
- **PATCH** `/agents/:agentId` → platformAgentsController.updateAgentMetadata
- **GET** `/agents/:agentId` → platformAgentsController.getAgentDetails
- **GET** `/agents/:agentId/analytics/channels` → `platformAnalyticsController`
- **GET** `/agents/:agentId/analytics/issues` → platformAnalyticsController.getIssues
- **POST** `/agents/:agentId/analytics/issues/:analysisId/reopen` → platformAnalyticsController.reopenQualityAlert
- **POST** `/agents/:agentId/analytics/issues/:analysisId/resolve` → platformAnalyticsController.resolveQualityAlert
- **GET** `/agents/:agentId/analytics/overview` → platformAnalyticsController.getOverview
- **GET** `/agents/:agentId/analytics/sentiment` → platformAnalyticsController.getSentiment
- **GET** `/agents/:agentId/analytics/timeline` → platformAnalyticsController.getTimeline
- **PATCH** `/agents/:agentId/config` → platformAgentsController.updateAgentConfig
- **GET** `/agents/:agentId/conversations` → platformAgentsController.getAgentConversations
- **DELETE** `/agents/:agentId/conversations/:conversationId` → platformAgentsController.deleteConversation
- **POST** `/agents/:agentId/conversations/:conversationId/close` → platformAgentsController.closeConversation
- **POST** `/agents/:agentId/integrations` → platformAgentsController.addAgentIntegration
- **GET** `/agents/:agentId/integrations` → platformAgentsController.getAgentIntegrations
- **DELETE** `/agents/:agentId/integrations/:integrationId` → platformAgentsController.deleteAgentIntegration
- **PUT** `/agents/:agentId/integrations/:integrationId` → platformAgentsController.updateAgentIntegration
- **POST** `/agents/:agentId/integrations/:integrationId/test` → platformAgentsController.testAgentIntegration
- **GET** `/agents/:agentId/knowledge` → platformAgentsController.getAgentKnowledge
- **DELETE** `/agents/:agentId/knowledge/:sourceId` → platformAgentsController.deleteAgentKnowledge
- **POST** `/agents/:agentId/knowledge/:sourceId/resync` → platformAgentsController.resyncKnowledgeSource
- **POST** `/agents/:agentId/knowledge/files` → platformAgentsController.uploadKnowledgeFiles
- **POST** `/agents/:agentId/knowledge/url` → platformAgentsController.addKnowledgeUrl
- **POST** `/agents/:agentId/knowledge/website/confirm` → platformAgentsController.confirmWebsitePages
- **POST** `/agents/:agentId/knowledge/website/discover` → platformAgentsController.discoverWebsite
- **POST** `/agents/:agentId/mcp` → platformAgentsController.attachMcpServerToAgent
- **GET** `/agents/:agentId/mcp` → platformAgentsController.getAgentMcpServers
- **DELETE** `/agents/:agentId/mcp/:attachmentId` → platformAgentsController.detachMcpServerFromAgent
- **PUT** `/agents/:agentId/mcp/:attachmentId` → platformAgentsController.updateAgentMcpServer
- **DELETE** `/agents/:agentId/messages/:messageId` → platformAgentsController.deleteMessage
- **GET** `/agents/:agentId/support/conversations/:conversationId` → platformSupportController.getHandoffDetail
- **POST** `/agents/:agentId/support/conversations/:conversationId/brief` → platformSupportController.generateAiStaffBrief
- **POST** `/agents/:agentId/support/conversations/:conversationId/reply` → platformSupportController.postSupportReply
- **POST** `/agents/:agentId/support/conversations/:conversationId/resolve` → platformSupportController.resolveHandoff
- …and 61 more

## `packages/api/src/modules/push/push.public.routes.ts`

- **POST** `/:orgId/subscribe` → `async`
- **POST** `/:orgId/unsubscribe` → `async`
- **GET** `/:orgId/vapid-public-key` → `async`
- **POST** `/click/:deliveryId` → `async`

## `packages/api/src/modules/push/push.routes.ts`

- **POST** `/connection/apns` → `async`
- **POST** `/connection/fcm` → `async`
- **POST** `/connection/webpush` → `async`
- **GET** `/subscribers` → `async`
- **POST** `/test` → `async`
- **GET** `/vapid-public-key` → `async`

## `packages/api/src/modules/reports/report.routes.ts`

- **POST** `/conversation/:conversationId` → reportController.fromConversation
- **POST** `/generate` → reportController.generate

## `packages/api/src/modules/roles/role.routes.ts`

- **POST** `/` → roleController.createRole
- **GET** `/` → roleController.getRoles
- **DELETE** `/:id` → roleController.deleteRole
- **PUT** `/:id` → roleController.updateRole

## `packages/api/src/modules/social/social.routes.ts`

- **GET** `/accounts` → `async`
- **POST** `/accounts/sync` → `async`
- **POST** `/posts` → `async`
- **GET** `/posts` → `async`
- **DELETE** `/posts/:id` → `async`
- **POST** `/posts/:id/publish` → `async`
- **POST** `/posts/:id/schedule` → `async`

## `packages/api/src/modules/splunk/splunk.routes.ts`

- **POST** `/agents/:agentId/connections` → splunkController.attachAgent
- **GET** `/agents/:agentId/connections` → splunkController.listAgentAttachments
- **DELETE** `/agents/:agentId/connections/:attachmentId` → splunkController.detachAgent
- **PUT** `/agents/:agentId/connections/:attachmentId` → splunkController.updateAttachment
- **POST** `/connections` → splunkController.createConnection
- **GET** `/connections` → splunkController.listConnections
- **DELETE** `/connections/:id` → splunkController.deleteConnection
- **PUT** `/connections/:id` → splunkController.updateConnection
- **GET** `/connections/:id` → splunkController.getConnection
- **POST** `/connections/:id/scan` → splunkController.scanConnection
- **POST** `/connections/:id/test` → splunkController.testConnection

## `packages/api/src/modules/team/team.routes.ts`

- **GET** `/` → teamController.getTeamMembers
- **DELETE** `/:userId` → teamController.removeMember
- **PUT** `/:userId/role` → teamController.updateMemberRole
- **POST** `/invite` → teamController.inviteMember

## `packages/api/src/services/dynatrace/__mock__/mockDynatraceServer.ts`

- **GET** `entitySelector`
- **GET** `entitySelector`
- **GET** `fields`
- **GET** `metricSelector`
- **GET** `pageSize`
- **GET** `problemSelector`
- **GET** `schemaIds`
- **GET** `sort`
- **GET** `text`

## `packages/api/src/services/elevenlabs/mcpServer.routes.ts`

- **DELETE** `/:agentId/mcp`
- **GET** `/:agentId/mcp`
- **POST** `/:agentId/mcp`

## `packages/api/src/services/splunk/__mock__/mockSplunkServer.ts`

- **GET** `search`

## `packages/platform-admin/src/screens/AiModelsPage.tsx`

- **PUT** `/api/platform/system-config/ai` → {
- **GET** `/api/platform/system-config/ai`

## `packages/platform-admin/src/screens/BillingPage.tsx`

- **GET** `/api/platform/billing/dashboard` → { params }
- **GET** `/api/platform/billing/orgs` → { params }

## `packages/platform-admin/src/screens/DashboardPage.tsx`

- **GET** `/api/platform/audit-logs?page=1&limit=5`
- **GET** `/api/platform/orgs`

## `packages/platform-admin/src/screens/DemoBookingPage.tsx`

- **GET** `/api/platform/booking/appointments` → { params: { scope: 'upcoming' } }
- **PUT** `/api/platform/booking/settings` → {
- **GET** `/api/platform/booking/settings`

## `packages/platform-admin/src/screens/FeaturesPage.tsx`

- **POST** `/api/platform/features`
- **GET** `/api/platform/features`

## `packages/platform-admin/src/screens/LoginPage.tsx`

- **POST** `/api/platform/auth/login` → { email, password }

## `packages/platform-admin/src/screens/OrgDetailPage.tsx`

- **GET** `/api/platform/plans/templates`

## `packages/platform-admin/src/screens/OrgsListPage.tsx`

- **POST** `/api/platform/orgs` → {
- **GET** `/api/platform/orgs`
- **GET** `q`

## `packages/platform-admin/src/screens/PlansPage.tsx`

- **GET** `/api/platform/features`
- **POST** `/api/platform/plans`
- **GET** `/api/platform/plans`

## `packages/platform-admin/src/screens/PlatformAdminsPage.tsx`

- **POST** `/api/platform/admins` → {
- **GET** `/api/platform/admins`

## `packages/platform-admin/src/screens/PricingConfigPage.tsx`

- **PUT** `/api/platform/billing/pricing` → { configs: rows }
- **GET** `/api/platform/billing/pricing`

## `packages/platform-admin/src/screens/SystemConfigPage.tsx`

- **GET** `/api/platform/system-config`

## `packages/platform-admin/src/screens/orgDetail/AuditTab.tsx`

- **GET** `/api/platform/audit-logs` → { params: { resourceId: orgId, limit: 100 } }

## `packages/platform-admin/src/screens/orgDetail/OrgFeaturesTab.tsx`

- **GET** `/api/platform/features`

## `packages/platform-admin/src/screens/orgDetail/agentDrawer/AgentDrawer.tsx`

- **GET** `/api/platform/system-config/ai`

## `packages/web/src/app/llms.txt/route.ts`

- **GET** `/llms.txt` → exported GET

## `packages/web/src/auth/ensureSessionBootstrapped.ts`

- **DELETE** `impersonate_token`
- **GET** `impersonate_token`

## `packages/web/src/components/agents/CreateAgentModal.tsx`

- **POST** `/agents` → { name, description }

## `packages/web/src/components/layout/DashboardLayout.tsx`

- **GET** `/agents`
- **POST** `/auth/logout`
- **GET** `/org/profile`

## `packages/web/src/components/layout/NotificationCenter.tsx`

- **GET** `/notifications`
- **POST** `/notifications/read-all`
- **GET** `/notifications/unread-count`

## `packages/web/src/components/settings/AlertRulesSection.tsx`

- **PUT** `/org/profile` → {
- **GET** `/org/profile`

## `packages/web/src/components/settings/AuditLogSection.tsx`

- **GET** `/org/audit-logs` → {

## `packages/web/src/components/settings/PrivacyDataSection.tsx`

- **GET** `/agents`
- **POST** `/org/gdpr/account-deletion`
- **POST** `/org/gdpr/erase-subject` → {
- **GET** `/org/gdpr/export` → { responseType: 'blob' }

## `packages/web/src/screens/AcceptInvitePage.tsx`

- **POST** `/auth/accept-invite` → { token, name, password }
- **GET** `token`

## `packages/web/src/screens/ConversationsPage.tsx`

- **GET** `conversationId`

## `packages/web/src/screens/DeliverabilityPage.tsx`

- **POST** `/outreach/email-domains` → payload
- **GET** `/outreach/email-domains`

## `packages/web/src/screens/DynatracePage.tsx`

- **POST** `/dynatrace/connections` → payload
- **GET** `/dynatrace/connections`

## `packages/web/src/screens/ForgotPasswordPage.tsx`

- **POST** `/auth/forgot-password` → { email }

## `packages/web/src/screens/IntegrationsPage.tsx`

- **GET** `/org/profile`

## `packages/web/src/screens/IssuesPage.tsx`

- **DELETE** `conversationId`
- **GET** `conversationId`

## `packages/web/src/screens/JourneysPage.tsx`

- **POST** `/outreach/journeys` → payload
- **GET** `/outreach/journeys`
- **GET** `/outreach/segments`

## `packages/web/src/screens/LoginPage.tsx`

- **POST** `/auth/login` → { email, password }

## `packages/web/src/screens/McpServersPage.tsx`

- **POST** `/mcp/servers` → payload
- **GET** `/mcp/servers`

## `packages/web/src/screens/OdooPage.tsx`

- **POST** `/odoo/connections` → payload
- **GET** `/odoo/connections`

## `packages/web/src/screens/OutreachPage.tsx`

- **POST** `/outreach/campaigns` → payload
- **GET** `/outreach/campaigns`
- **GET** `/outreach/lists`
- **POST** `/outreach/lists` → fd
- **GET** `/outreach/lists`
- **POST** `/outreach/lists/manual` → {
- **GET** `/outreach/segments`

## `packages/web/src/screens/PlaygroundPage.tsx`

- **POST** `/reports/generate` → { responseType: 'blob' }

## `packages/web/src/screens/RegisterPage.tsx`

- **POST** `/auth/register` → {

## `packages/web/src/screens/ResetPasswordPage.tsx`

- **POST** `/auth/reset-password` → { token, password }
- **GET** `token`

## `packages/web/src/screens/SegmentsPage.tsx`

- **POST** `/outreach/segments` → payload
- **GET** `/outreach/segments`
- **POST** `/outreach/segments/preview` → {

## `packages/web/src/screens/SettingsPage.tsx`

- **POST** `/org/logo` → fd
- **PUT** `/org/profile` → {
- **GET** `/org/profile`

## `packages/web/src/screens/SplunkPage.tsx`

- **POST** `/splunk/connections` → payload
- **GET** `/splunk/connections`

## `packages/web/src/screens/SupportInboxPage.tsx`

- **GET** `conversationId`

## `packages/web/src/screens/TeamPage.tsx`

- **GET** `/roles`
- **GET** `/team`
- **POST** `/team/invite`

## `packages/web/src/screens/VerifyEmailPage.tsx`

- **POST** `/auth/resend-verification` → { email }
- **POST** `/auth/verify-email` → { email, code }
- **GET** `email`

## `packages/web/src/screens/odoo/OdooOperationsPanel.tsx`

- **GET** `/odoo/operations` → {

## `packages/web/src/services/integrationsV2.ts`

- **GET** `/integrations/catalog`
- **GET** `/integrations/connections`
- **POST** `/integrations/oauth/email-bridge/connect` → body
- **GET** `/integrations/oauth/meta/byoa-info`
- **GET** `/integrations/oauth/meta/config`
- **POST** `/integrations/oauth/meta/exchange` → body
- **POST** `/integrations/oauth/teams/connect` → body

## `test_chat.ts`

- **POST** `https://botifyarabia.ai/api/chat/1bd578a4-9bda-425d-8765-eb0903463bef` → {
