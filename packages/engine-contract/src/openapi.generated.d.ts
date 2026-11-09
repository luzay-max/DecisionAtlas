// Generated from Engine OpenAPI. Run pnpm contract:generate; do not edit.
export interface paths {
    "/auth/bootstrap": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Bootstrap Auth */
        post: operations["bootstrap_auth_auth_bootstrap_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Login */
        post: operations["login_auth_login_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/auth/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Logout Auth */
        post: operations["logout_auth_auth_logout_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/auth/scope": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Switch Scope */
        post: operations["switch_scope_auth_scope_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/auth/session": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Session */
        get: operations["get_session_auth_session_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/dashboard/summary": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Dashboard Summary */
        get: operations["get_dashboard_summary_dashboard_summary_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/decisions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Decisions */
        get: operations["list_decisions_decisions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/decisions/{decision_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Decision */
        get: operations["get_decision_decisions__decision_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/decisions/{decision_id}/review": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Review Decision */
        post: operations["review_decision_decisions__decision_id__review_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/drift": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Drift Alerts */
        get: operations["list_drift_alerts_drift_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/drift/alerts/{alert_id}/disposition": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Update Drift Alert Disposition */
        post: operations["update_drift_alert_disposition_drift_alerts__alert_id__disposition_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/drift/evaluate": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Evaluate Drift */
        post: operations["evaluate_drift_drift_evaluate_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/governance/documents": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Governance Documents */
        get: operations["list_governance_documents_governance_documents_get"];
        put?: never;
        /** Create Governance Document */
        post: operations["create_governance_document_governance_documents_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/governance/guardrail": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Governance Guardrail */
        get: operations["get_governance_guardrail_governance_guardrail_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/governance/rules": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Governance Rules */
        get: operations["list_governance_rules_governance_rules_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/governance/rules/{draft_id}/lifecycle": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Update Governance Rule Lifecycle */
        post: operations["update_governance_rule_lifecycle_governance_rules__draft_id__lifecycle_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/governance/rules/{draft_id}/review": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Review Governance Rule */
        post: operations["review_governance_rule_governance_rules__draft_id__review_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Healthcheck */
        get: operations["healthcheck_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/capabilities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Import Capabilities
         * @description Expose the effective control-plane capability without mutating job state.
         */
        get: operations["get_import_capabilities_imports_capabilities_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/git-sources/bind": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Bind Git Source */
        post: operations["bind_git_source_imports_git_sources_bind_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/github": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Import Github */
        post: operations["import_github_imports_github_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/github/installations/bind": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Bind Installation */
        post: operations["bind_installation_imports_github_installations_bind_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/github/private-access/bind": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Bind Private Access */
        post: operations["bind_private_access_imports_github_private_access_bind_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/github/webhook": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Github Webhook */
        post: operations["github_webhook_imports_github_webhook_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/lookup": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Lookup Import Target */
        get: operations["lookup_import_target_imports_lookup_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/{job_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Import Job */
        get: operations["get_import_job_imports__job_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/{job_id}/pause": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Pause Import Job */
        post: operations["pause_import_job_imports__job_id__pause_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/imports/{job_id}/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Resume Import Job */
        post: operations["resume_import_job_imports__job_id__resume_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/query/why": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Query Why */
        post: operations["query_why_query_why_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/runtime/provider-mode": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Provider Mode */
        get: operations["get_provider_mode_runtime_provider_mode_get"];
        put?: never;
        /** Set Provider Mode */
        post: operations["set_provider_mode_runtime_provider_mode_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/team/accounts": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Team Accounts */
        get: operations["list_team_accounts_team_accounts_get"];
        put?: never;
        /** Create Team Account */
        post: operations["create_team_account_team_accounts_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/team/accounts/{actor_id}/disable": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Disable Team Account */
        post: operations["disable_team_account_team_accounts__actor_id__disable_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/team/accounts/{actor_id}/reset-password": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Reset Team Account Password */
        post: operations["reset_team_account_password_team_accounts__actor_id__reset_password_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/team/accounts/{actor_id}/role": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Update Team Account Role */
        post: operations["update_team_account_role_team_accounts__actor_id__role_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/team/workspaces/{workspace_slug}/members": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Workspace Members */
        get: operations["list_workspace_members_team_workspaces__workspace_slug__members_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/team/workspaces/{workspace_slug}/members/{actor_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /** Assign Workspace Member */
        put: operations["assign_workspace_member_team_workspaces__workspace_slug__members__actor_id__put"];
        post?: never;
        /** Remove Workspace Member */
        delete: operations["remove_workspace_member_team_workspaces__workspace_slug__members__actor_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/timeline": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Timeline */
        get: operations["get_timeline_timeline_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AuthBootstrapActorResponse */
        AuthBootstrapActorResponse: {
            /** Bootstrap */
            bootstrap: boolean;
            /** Id */
            id: number;
            /**
             * Status
             * @enum {string}
             */
            status: "active" | "disabled";
            /** Username */
            username: string;
        };
        /** AuthBootstrapResponse */
        AuthBootstrapResponse: {
            actor: components["schemas"]["AuthBootstrapActorResponse"];
            /** Current Owner Scope */
            current_owner_scope: string;
            /** Role */
            role: "viewer" | "reviewer" | "admin";
            /** Session Token */
            session_token: string;
        };
        /** AuthLoginResponse */
        AuthLoginResponse: {
            actor: components["schemas"]["AuthBootstrapActorResponse"];
            available_scopes: components["schemas"]["AuthOwnerScopeMembershipResponse"][];
            /** Current Owner Scope */
            current_owner_scope: string;
            /** Role */
            role: "viewer" | "reviewer" | "admin";
            /** Session Token */
            session_token: string;
        };
        /** AuthLogoutResponse */
        AuthLogoutResponse: {
            /**
             * Status
             * @enum {string}
             */
            status: "signed_out";
        };
        /** AuthOwnerScopeMembershipResponse */
        AuthOwnerScopeMembershipResponse: {
            /** Owner Scope */
            owner_scope: string;
            /**
             * Role
             * @enum {string}
             */
            role: "viewer" | "reviewer" | "admin";
        };
        /** AuthSessionActorResponse */
        AuthSessionActorResponse: {
            /** Bootstrap */
            bootstrap: boolean;
            /** Id */
            id: number;
            /** Username */
            username: string;
        };
        /** AuthSessionResponse */
        AuthSessionResponse: {
            actor: components["schemas"]["AuthSessionActorResponse"];
            available_scopes: components["schemas"]["AuthOwnerScopeMembershipResponse"][];
            /** Current Owner Scope */
            current_owner_scope: string;
            /** Role */
            role: "viewer" | "reviewer" | "admin";
            /** Session Token */
            session_token: string;
        };
        /** DecisionArtifactSummaryResponse */
        DecisionArtifactSummaryResponse: {
            /** Id */
            id: number;
            /** Repo */
            repo: string | null;
            /** Title */
            title: string | null;
            /** Type */
            type: string;
            /** Url */
            url: string | null;
        };
        /** DecisionAuditEventResponse */
        DecisionAuditEventResponse: {
            /** Action */
            action: string;
            /** Actor Id */
            actor_id: number | null;
            /** Actor Role */
            actor_role: string;
            /** Actor Username */
            actor_username: string;
            /** Created At */
            created_at: string | null;
            /** Id */
            id: number;
            /** Metadata */
            metadata: {
                [key: string]: unknown;
            } | null;
            /** New State */
            new_state: {
                [key: string]: unknown;
            } | null;
            /** Owner Scope */
            owner_scope: string;
            /** Previous State */
            previous_state: {
                [key: string]: unknown;
            } | null;
            /** Rationale */
            rationale: string | null;
            /** Target Id */
            target_id: number;
            /** Target Type */
            target_type: string;
            /** Workspace Id */
            workspace_id: number | null;
        };
        /** DecisionCandidateQualityResponse */
        DecisionCandidateQualityResponse: {
            /**
             * Confidence Bucket
             * @enum {string}
             */
            confidence_bucket: "high" | "medium" | "low";
            /** Has Primary Artifact */
            has_primary_artifact: boolean;
            /** Has Source Url */
            has_source_url: boolean;
            /**
             * Label
             * @enum {string}
             */
            label: "strong" | "partial" | "thin";
            /** Previewable Source Ref Count */
            previewable_source_ref_count: number;
            /** Reasons */
            reasons: string[];
            /** Source Ref Count */
            source_ref_count: number;
            /** Summary */
            summary: string;
        };
        /** DecisionDetailResponse */
        DecisionDetailResponse: {
            candidate_quality: components["schemas"]["DecisionCandidateQualityResponse"];
            /** Chosen Option */
            chosen_option: string;
            /** Confidence */
            confidence: number;
            /** Constraints */
            constraints: string | null;
            /** Context */
            context: string | null;
            /** Id */
            id: number;
            /** Problem */
            problem: string;
            review_evidence: components["schemas"]["DecisionReviewEvidenceResponse"];
            /** Review History */
            review_history: components["schemas"]["DecisionAuditEventResponse"][];
            /** Review State */
            review_state: string;
            /** Source Refs */
            source_refs: components["schemas"]["DecisionSourceRefResponse"][];
            /** Source Summary */
            source_summary: string;
            /** Status */
            status: string;
            /** Title */
            title: string;
            /** Tradeoffs */
            tradeoffs: string;
            /** Workspace Id */
            workspace_id: number;
            /**
             * Workspace Mode
             * @enum {string}
             */
            workspace_mode: "demo" | "imported" | "mixed";
        };
        /** DecisionListItemResponse */
        DecisionListItemResponse: {
            candidate_quality: components["schemas"]["DecisionCandidateQualityResponse"];
            /** Chosen Option */
            chosen_option: string;
            /** Confidence */
            confidence: number;
            /** Constraints */
            constraints: string | null;
            /** Context */
            context: string | null;
            /** Id */
            id: number;
            /** Problem */
            problem: string;
            review_evidence: components["schemas"]["DecisionReviewEvidenceResponse"];
            /** Review State */
            review_state: string;
            /** Source Summary */
            source_summary: string;
            /** Status */
            status: string;
            /** Title */
            title: string;
            /** Tradeoffs */
            tradeoffs: string;
            /** Workspace Id */
            workspace_id: number;
            /**
             * Workspace Mode
             * @enum {string}
             */
            workspace_mode: "demo" | "imported" | "mixed";
        };
        /** DecisionQuoteIntegrityResponse */
        DecisionQuoteIntegrityResponse: {
            /** Found Count */
            found_count: number;
            /** Missing Count */
            missing_count: number;
            /**
             * Status
             * @enum {string}
             */
            status: "no_refs" | "current_quote_missing" | "unverifiable" | "current_quotes_found";
            /** Unverifiable Count */
            unverifiable_count: number;
        };
        /** DecisionReviewEvidenceResponse */
        DecisionReviewEvidenceResponse: {
            current_quote_integrity: components["schemas"]["DecisionQuoteIntegrityResponse"];
            primary_artifact: components["schemas"]["DecisionArtifactSummaryResponse"] | null;
            /** Source Ref Count */
            source_ref_count: number;
            /** Source Ref Preview */
            source_ref_preview: components["schemas"]["DecisionSourceRefResponse"][];
            /**
             * State
             * @enum {string}
             */
            state: "grounded" | "thin" | "missing";
        };
        /** DecisionReviewResponse */
        DecisionReviewResponse: {
            audit_event: components["schemas"]["DecisionAuditEventResponse"];
            /** Chosen Option */
            chosen_option: string;
            /** Confidence */
            confidence: number;
            /** Constraints */
            constraints: string | null;
            /** Context */
            context: string | null;
            /** Id */
            id: number;
            /** Problem */
            problem: string;
            /** Review History */
            review_history: components["schemas"]["DecisionAuditEventResponse"][];
            /** Review State */
            review_state: string;
            /** Status */
            status: string;
            /** Title */
            title: string;
            /** Tradeoffs */
            tradeoffs: string;
            /** Workspace Id */
            workspace_id: number;
        };
        /** DecisionSourceRefResponse */
        DecisionSourceRefResponse: {
            /** Artifact Id */
            artifact_id: number;
            /** Current Quote Match */
            current_quote_match: boolean | null;
            /** Id */
            id: number;
            /** Quote */
            quote: string;
            /** Relevance Score */
            relevance_score: number | null;
            /** Span End */
            span_end: number | null;
            /** Span Start */
            span_start: number | null;
            /** Url */
            url: string | null;
        };
        /** DriftDispositionRequest */
        DriftDispositionRequest: {
            /** Rationale */
            rationale?: string | null;
            /** Status */
            status: string;
        };
        /** GitHubImportRequest */
        GitHubImportRequest: {
            /** Access Source Ref */
            access_source_ref?: string | null;
            /** Access Source Type */
            access_source_type?: string | null;
            /**
             * Mode
             * @default full
             */
            mode?: string;
            /** Owner Scope */
            owner_scope?: string | null;
            /** Repo */
            repo: string;
            /** Workspace Slug */
            workspace_slug?: string | null;
        };
        /** GitHubInstallationBindingRequest */
        GitHubInstallationBindingRequest: {
            /** Account Login */
            account_login?: string | null;
            /** Account Type */
            account_type?: string | null;
            /** Installation Id */
            installation_id: string;
            /** Owner Scope */
            owner_scope?: string | null;
            /** Repo */
            repo: string;
            /** Workspace Slug */
            workspace_slug?: string | null;
        };
        /** GitHubPrivateAccessBindingRequest */
        GitHubPrivateAccessBindingRequest: {
            /** Owner Scope */
            owner_scope?: string | null;
            /** Repo */
            repo: string;
            /** Source Label */
            source_label?: string | null;
            /** Source Ref */
            source_ref?: string | null;
            /** Token */
            token: string;
            /** Workspace Slug */
            workspace_slug?: string | null;
        };
        /** GitHubWebhookResponse */
        GitHubWebhookResponse: {
            /** Action */
            action: string | null;
            /** Delivery Id */
            delivery_id: string | null;
            /** Event */
            event: string;
            /** Installation Id */
            installation_id: string | null;
            /** Job Id */
            job_id?: string | null;
            /** Owner Scope */
            owner_scope?: string | null;
            /** Reason */
            reason?: string | null;
            /** Repo */
            repo: string | null;
            /**
             * Status
             * @enum {string}
             */
            status: "ignored" | "queued";
            /** Sync Origin */
            sync_origin?: string | null;
            /** Trigger Event */
            trigger_event?: string | null;
            /** Workspace Slug */
            workspace_slug?: string | null;
        };
        /** GitSourceBindingRequest */
        GitSourceBindingRequest: {
            /** Access Mode */
            access_mode: string;
            /** Provider */
            provider: string;
            /** Repo */
            repo: string;
            /** Source Label */
            source_label?: string | null;
            /** Source Ref */
            source_ref?: string | null;
            /** Token */
            token?: string | null;
            /** Workspace Slug */
            workspace_slug?: string | null;
        };
        /** GovernanceDocumentImportRequest */
        GovernanceDocumentImportRequest: {
            /** Content */
            content: string;
            /** Document Type */
            document_type: string;
            /**
             * Scope
             * @default all
             */
            scope?: string;
            /** Source Path */
            source_path?: string | null;
            /**
             * Status
             * @default active
             */
            status?: string;
            /** Title */
            title: string;
        };
        /** GovernanceRuleLifecycleRequest */
        GovernanceRuleLifecycleRequest: {
            /** Lifecycle Rationale */
            lifecycle_rationale?: string | null;
            /** Lifecycle Status */
            lifecycle_status: string;
            /** Superseded By Rule Id */
            superseded_by_rule_id?: number | null;
        };
        /** GovernanceRuleReviewRequest */
        GovernanceRuleReviewRequest: {
            /** Review Rationale */
            review_rationale?: string | null;
            /** Review State */
            review_state: string;
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** ImportCapabilitiesResponse */
        ImportCapabilitiesResponse: {
            pause_resume: components["schemas"]["ImportPauseResumeCapabilityResponse"];
        };
        /** ImportJobResponse */
        ImportJobResponse: {
            /** Error Message */
            error_message?: string | null;
            /** Finished At */
            finished_at?: string | null;
            /** Imported Count */
            imported_count: number;
            /** Job Id */
            job_id: string;
            /**
             * Mode
             * @enum {string}
             */
            mode: "full" | "since_last_sync";
            /** Repo */
            repo: string;
            /** Started At */
            started_at?: string | null;
            /**
             * Status
             * @enum {string}
             */
            status: "queued" | "running" | "paused" | "succeeded" | "failed";
            /** Summary */
            summary?: {
                [key: string]: unknown;
            } | null;
            /** Sync Origin */
            sync_origin?: string | null;
            /** Trigger Event */
            trigger_event?: string | null;
            /** Workspace Slug */
            workspace_slug: string | null;
        };
        /** ImportPauseResumeCapabilityResponse */
        ImportPauseResumeCapabilityResponse: {
            /** Enabled */
            enabled: boolean;
            /** Reason Code */
            reason_code: "worker_lifecycle_unverified" | null;
        };
        /** ImportTargetResponse */
        ImportTargetResponse: {
            /** Access Mode */
            access_mode: string;
            /** Access Requirement */
            access_requirement?: string | null;
            /** Access Requirement Detail */
            access_requirement_detail?: string | null;
            /** Access Source Label */
            access_source_label: string;
            /** Access Source Status */
            access_source_status?: string | null;
            /** Access Source Status Detail */
            access_source_status_detail?: string | null;
            /** Access Source Type */
            access_source_type: string;
            active_import: components["schemas"]["ImportJobResponse"] | null;
            /** Can Incremental Sync */
            can_incremental_sync: boolean;
            /** Has Running Import */
            has_running_import: boolean;
            /** Has Successful Import */
            has_successful_import: boolean;
            /** Last Import Summary */
            last_import_summary?: {
                [key: string]: unknown;
            } | null;
            latest_import: components["schemas"]["ImportJobResponse"] | null;
            /** Latest Sync At */
            latest_sync_at?: string | null;
            /** Latest Sync Origin */
            latest_sync_origin?: string | null;
            /** Next Action */
            next_action?: string | null;
            /** Owner Scope */
            owner_scope: string;
            /** Provider */
            provider: string;
            /** Repo */
            repo: string;
            /** Repo Private */
            repo_private?: boolean | null;
            /** Repo Url */
            repo_url: string | null;
            /** Setup Outcome */
            setup_outcome?: string | null;
            /** Workspace Exists */
            workspace_exists: boolean;
            /** Workspace Slug */
            workspace_slug: string | null;
        };
        /** LoginRequest */
        LoginRequest: {
            /** Password */
            password: string;
            /** Username */
            username: string;
        };
        /** ProviderModeRequest */
        ProviderModeRequest: {
            /** Mode */
            mode: string;
        };
        /** RecentSync */
        RecentSync: {
            /** Finished At */
            finished_at?: string | null;
            /** Job Id */
            job_id: string;
            /** Mode */
            mode: string;
            /** Started At */
            started_at?: string | null;
            /** Status */
            status: string;
            /** Sync Origin */
            sync_origin?: string | null;
            /** Trigger Event */
            trigger_event?: string | null;
        };
        /** ReviewDecisionRequest */
        ReviewDecisionRequest: {
            /** Review Rationale */
            review_rationale?: string | null;
            /** Review State */
            review_state: string;
        };
        /** ScopeSwitchRequest */
        ScopeSwitchRequest: {
            /** Owner Scope */
            owner_scope: string;
        };
        /** TeamAccountCreateRequest */
        TeamAccountCreateRequest: {
            /** Display Name */
            display_name?: string | null;
            /** Password */
            password: string;
            /**
             * Role
             * @default viewer
             */
            role?: string;
            /** Username */
            username: string;
        };
        /** TeamAccountListResponse */
        TeamAccountListResponse: {
            /** Accounts */
            accounts: components["schemas"]["TeamAccountResponse"][];
        };
        /** TeamAccountMutationResponse */
        TeamAccountMutationResponse: {
            account: components["schemas"]["TeamAccountResponse"];
        };
        /** TeamAccountPasswordResetRequest */
        TeamAccountPasswordResetRequest: {
            /** Password */
            password: string;
        };
        /** TeamAccountResponse */
        TeamAccountResponse: {
            /** Bootstrap */
            bootstrap: boolean;
            /** Display Name */
            display_name: string | null;
            /** Id */
            id: number;
            /**
             * Role
             * @enum {string}
             */
            role: "viewer" | "reviewer" | "admin";
            /**
             * Status
             * @enum {string}
             */
            status: "active" | "disabled";
            /** Username */
            username: string;
        };
        /** TeamAccountRoleRequest */
        TeamAccountRoleRequest: {
            /** Role */
            role: string;
        };
        /** TeamWorkspaceActorResponse */
        TeamWorkspaceActorResponse: {
            /** Bootstrap */
            bootstrap: boolean;
            /** Display Name */
            display_name: string | null;
            /** Id */
            id: number;
            /** Role */
            role: "viewer" | "reviewer" | "admin" | null;
            /**
             * Status
             * @enum {string}
             */
            status: "active" | "disabled";
            /** Username */
            username: string;
        };
        /** TeamWorkspaceMemberMutationResponse */
        TeamWorkspaceMemberMutationResponse: {
            member: components["schemas"]["TeamWorkspaceMemberResponse"];
        };
        /** TeamWorkspaceMemberRemovalResponse */
        TeamWorkspaceMemberRemovalResponse: {
            /** Removed */
            removed: boolean;
        };
        /** TeamWorkspaceMemberResponse */
        TeamWorkspaceMemberResponse: {
            actor: components["schemas"]["TeamWorkspaceActorResponse"];
            /**
             * Role
             * @enum {string}
             */
            role: "viewer" | "reviewer" | "admin";
            /** Workspace Id */
            workspace_id: number;
        };
        /** TeamWorkspaceMembersResponse */
        TeamWorkspaceMembersResponse: {
            /** Members */
            members: components["schemas"]["TeamWorkspaceMemberResponse"][];
            /** Workspace Slug */
            workspace_slug: string;
        };
        /** ValidationError */
        ValidationError: {
            /** Context */
            ctx?: Record<string, never>;
            /** Input */
            input?: unknown;
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
        };
        /** WhyAnswerContext */
        WhyAnswerContext: {
            retrieval?: components["schemas"]["WhyRetrievalDiagnostics"] | null;
            /**
             * Retrieval Mode
             * @default not_run
             * @enum {string}
             */
            retrieval_mode?: "not_run" | "hybrid" | "lexical_only" | "lexical_fallback";
            /** Source Summary */
            source_summary: string;
            /**
             * Workspace Mode
             * @enum {string}
             */
            workspace_mode: "demo" | "imported" | "mixed";
            workspace_readiness?: components["schemas"]["WorkspaceReadiness"] | null;
        };
        /** WhyAnswerResponse */
        WhyAnswerResponse: {
            /** Answer */
            answer: string;
            answer_context: components["schemas"]["WhyAnswerContext"];
            /** Citations */
            citations: components["schemas"]["WhyCitation"][];
            primary_decision?: components["schemas"]["WhyPrimaryDecision"] | null;
            /** Question */
            question: string;
            /**
             * Retrieval Mode
             * @default not_run
             * @enum {string}
             */
            retrieval_mode?: "not_run" | "hybrid" | "lexical_only" | "lexical_fallback";
            /**
             * Status
             * @enum {string}
             */
            status: "ok" | "limited_support" | "insufficient_evidence" | "review_required" | "evidence_limited" | "analysis_failed";
            /** Supporting Context */
            supporting_context?: components["schemas"]["WhySupportingContext"][];
        };
        /** WhyCitation */
        WhyCitation: {
            /** Decision Id */
            decision_id?: number | null;
            /** Quote */
            quote: string;
            /** Source Ref Id */
            source_ref_id?: number | null;
            /** Url */
            url: string | null;
        };
        /**
         * WhyHTTPError
         * @description Existing HTTPException envelope; validation errors retain FastAPI's 422 model.
         */
        WhyHTTPError: {
            /** Detail */
            detail: string;
        };
        /** WhyPrimaryDecision */
        WhyPrimaryDecision: {
            /** Decision Id */
            decision_id: number;
            /** Title */
            title: string;
        };
        /** WhyQueryRequest */
        WhyQueryRequest: {
            /** Question */
            question: string;
            /** Workspace Slug */
            workspace_slug: string;
        };
        /** WhyRetrievalDiagnostics */
        WhyRetrievalDiagnostics: {
            /**
             * Decision Overlap
             * @default 0
             */
            decision_overlap?: number;
            /**
             * Raw Score
             * @default 0
             */
            raw_score?: number;
            /**
             * Source Ref Overlap
             * @default 0
             */
            source_ref_overlap?: number;
            /**
             * Structural Fit
             * @default 0
             */
            structural_fit?: number;
            /** Support Reasons */
            support_reasons: string[];
        };
        /** WhySupportingContext */
        WhySupportingContext: {
            /** Answer */
            answer: string;
            /** Decision Id */
            decision_id: number;
            /** Title */
            title: string;
        };
        /** WorkspaceMemberRoleRequest */
        WorkspaceMemberRoleRequest: {
            /** Role */
            role: string;
        };
        /** WorkspaceReadiness */
        WorkspaceReadiness: {
            /**
             * Accepted Baseline Established
             * @default false
             */
            accepted_baseline_established?: boolean;
            /**
             * Accepted Decision Count
             * @default 0
             */
            accepted_decision_count?: number;
            /**
             * Access Source Label
             * @default
             */
            access_source_label?: string;
            /** Access Source Status */
            access_source_status?: string | null;
            /** Access Source Status Detail */
            access_source_status_detail?: string | null;
            /**
             * Access Source Type
             * @default public
             */
            access_source_type?: string;
            /** Active Import Job Id */
            active_import_job_id?: string | null;
            /** Active Import Mode */
            active_import_mode?: string | null;
            /** Active Import Status */
            active_import_status?: string | null;
            /** Active Sync Origin */
            active_sync_origin?: string | null;
            /**
             * Candidate Decision Count
             * @default 0
             */
            candidate_decision_count?: number;
            /** Drift State */
            drift_state: string;
            /** Latest Sync At */
            latest_sync_at?: string | null;
            /** Latest Sync Origin */
            latest_sync_origin?: string | null;
            /** Next Action */
            next_action: string;
            /** Recent Syncs */
            recent_syncs?: components["schemas"]["RecentSync"][];
            /** Recommended Actions */
            recommended_actions: string[];
            /** Review State */
            review_state: string;
            /** State */
            state: string;
            /** Why State */
            why_state: string;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    bootstrap_auth_auth_bootstrap_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthBootstrapResponse"];
                };
            };
        };
    };
    login_auth_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LoginRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthLoginResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    logout_auth_auth_logout_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthLogoutResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    switch_scope_auth_scope_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ScopeSwitchRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthSessionResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_session_auth_session_get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthSessionResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_dashboard_summary_dashboard_summary_get: {
        parameters: {
            query: {
                workspace_slug: string;
            };
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_decisions_decisions_get: {
        parameters: {
            query: {
                workspace_slug: string;
                review_state?: string | null;
            };
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DecisionListItemResponse"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_decision_decisions__decision_id__get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                decision_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DecisionDetailResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    review_decision_decisions__decision_id__review_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                decision_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ReviewDecisionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DecisionReviewResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_drift_alerts_drift_get: {
        parameters: {
            query: {
                workspace_slug: string;
            };
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_drift_alert_disposition_drift_alerts__alert_id__disposition_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                alert_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DriftDispositionRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    evaluate_drift_drift_evaluate_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": {
                    [key: string]: unknown;
                };
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_governance_documents_governance_documents_get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_governance_document_governance_documents_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GovernanceDocumentImportRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_governance_guardrail_governance_guardrail_get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_governance_rules_governance_rules_get: {
        parameters: {
            query?: {
                review_state?: string | null;
            };
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_governance_rule_lifecycle_governance_rules__draft_id__lifecycle_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                draft_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GovernanceRuleLifecycleRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    review_governance_rule_governance_rules__draft_id__review_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                draft_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GovernanceRuleReviewRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    healthcheck_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: boolean;
                    };
                };
            };
        };
    };
    get_import_capabilities_imports_capabilities_get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportCapabilitiesResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    bind_git_source_imports_git_sources_bind_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GitSourceBindingRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportTargetResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    import_github_imports_github_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GitHubImportRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportJobResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    bind_installation_imports_github_installations_bind_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GitHubInstallationBindingRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportTargetResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    bind_private_access_imports_github_private_access_bind_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GitHubPrivateAccessBindingRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportTargetResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    github_webhook_imports_github_webhook_post: {
        parameters: {
            query?: never;
            header: {
                "x-github-event": string;
                "x-github-delivery"?: string | null;
                "x-hub-signature-256"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GitHubWebhookResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    lookup_import_target_imports_lookup_get: {
        parameters: {
            query: {
                repo: string;
            };
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportTargetResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_import_job_imports__job_id__get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportJobResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    pause_import_job_imports__job_id__pause_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportJobResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    resume_import_job_imports__job_id__resume_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ImportJobResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    query_why_query_why_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["WhyQueryRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhyAnswerResponse"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhyHTTPError"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhyHTTPError"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhyHTTPError"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
            /** @description Bad Gateway */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhyHTTPError"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WhyHTTPError"];
                };
            };
        };
    };
    get_provider_mode_runtime_provider_mode_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
        };
    };
    set_provider_mode_runtime_provider_mode_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProviderModeRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_team_accounts_team_accounts_get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamAccountListResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_team_account_team_accounts_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TeamAccountCreateRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamAccountMutationResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    disable_team_account_team_accounts__actor_id__disable_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                actor_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamAccountMutationResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    reset_team_account_password_team_accounts__actor_id__reset_password_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                actor_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TeamAccountPasswordResetRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamAccountMutationResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_team_account_role_team_accounts__actor_id__role_post: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                actor_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TeamAccountRoleRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamAccountMutationResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_workspace_members_team_workspaces__workspace_slug__members_get: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                workspace_slug: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamWorkspaceMembersResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    assign_workspace_member_team_workspaces__workspace_slug__members__actor_id__put: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                workspace_slug: string;
                actor_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["WorkspaceMemberRoleRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamWorkspaceMemberMutationResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    remove_workspace_member_team_workspaces__workspace_slug__members__actor_id__delete: {
        parameters: {
            query?: never;
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path: {
                workspace_slug: string;
                actor_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TeamWorkspaceMemberRemovalResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_timeline_timeline_get: {
        parameters: {
            query: {
                workspace_slug: string;
            };
            header?: {
                "x-decisionatlas-session-token"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: unknown;
                    };
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
}
