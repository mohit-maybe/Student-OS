CREATE TABLE `auditEvents` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int,
	`eventType` varchar(96) NOT NULL,
	`entityType` varchar(96) NOT NULL,
	`entityId` varchar(96) NOT NULL,
	`details` json,
	`occurredAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `auditEvents_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `intelligenceSignals` (
	`id` int AUTO_INCREMENT NOT NULL,
	`newsItemId` int NOT NULL,
	`assetSymbol` varchar(32) NOT NULL,
	`assetClass` enum('equity','crypto','etf','macro') NOT NULL,
	`catalyst` varchar(96) NOT NULL,
	`direction` enum('upside','downside','mixed','watch') NOT NULL,
	`sentiment` enum('positive','negative','neutral','mixed') NOT NULL,
	`confidence` int NOT NULL,
	`hypothesis` text NOT NULL,
	`uncertainty` text NOT NULL,
	`evidenceExcerpt` text NOT NULL,
	`informationCutoffAt` timestamp NOT NULL,
	`modelName` varchar(96) NOT NULL,
	`promptVersion` varchar(32) NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `intelligenceSignals_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `newsItems` (
	`id` int AUTO_INCREMENT NOT NULL,
	`sourceId` int,
	`providerItemId` varchar(512) NOT NULL,
	`canonicalUrl` varchar(2048) NOT NULL,
	`title` text NOT NULL,
	`summary` text,
	`author` varchar(255),
	`publisher` varchar(255),
	`publisherUrl` varchar(2048),
	`imageUrl` varchar(2048),
	`language` varchar(32),
	`publishedAt` timestamp,
	`acquiredAt` timestamp NOT NULL DEFAULT (now()),
	`contentFingerprint` varchar(128) NOT NULL,
	`rawPayload` json,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `newsItems_id` PRIMARY KEY(`id`),
	CONSTRAINT `newsItems_provider_fingerprint_unique` UNIQUE(`providerItemId`,`contentFingerprint`)
);
--> statement-breakpoint
CREATE TABLE `newsSources` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int,
	`provider` varchar(64) NOT NULL,
	`displayName` varchar(160) NOT NULL,
	`kind` enum('gdelt','rss','api') NOT NULL,
	`baseUrl` varchar(2048) NOT NULL,
	`connectionStatus` enum('connected','attention','unconfigured') NOT NULL DEFAULT 'unconfigured',
	`enabled` boolean NOT NULL DEFAULT true,
	`lastFetchedAt` timestamp,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `newsSources_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `paperAccounts` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`baseCurrency` varchar(8) NOT NULL DEFAULT 'USD',
	`virtualCash` decimal(18,2) NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `paperAccounts_id` PRIMARY KEY(`id`),
	CONSTRAINT `paperAccounts_user_unique` UNIQUE(`userId`)
);
--> statement-breakpoint
CREATE TABLE `paperOrders` (
	`id` int AUTO_INCREMENT NOT NULL,
	`accountId` int NOT NULL,
	`signalId` int,
	`symbol` varchar(32) NOT NULL,
	`assetClass` enum('equity','crypto','etf') NOT NULL,
	`side` enum('buy','sell') NOT NULL,
	`quantity` decimal(18,6) NOT NULL,
	`requestedPrice` decimal(18,6) NOT NULL,
	`fillPrice` decimal(18,6),
	`status` enum('queued','filled','cancelled','rejected') NOT NULL DEFAULT 'queued',
	`rationale` text NOT NULL,
	`informationCutoffAt` timestamp NOT NULL,
	`submittedAt` timestamp NOT NULL DEFAULT (now()),
	`filledAt` timestamp,
	CONSTRAINT `paperOrders_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `paperPositions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`accountId` int NOT NULL,
	`symbol` varchar(32) NOT NULL,
	`assetClass` enum('equity','crypto','etf') NOT NULL,
	`quantity` decimal(18,6) NOT NULL,
	`averagePrice` decimal(18,6) NOT NULL,
	`markPrice` decimal(18,6) NOT NULL,
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `paperPositions_id` PRIMARY KEY(`id`),
	CONSTRAINT `paperPositions_account_symbol_unique` UNIQUE(`accountId`,`symbol`)
);
--> statement-breakpoint
CREATE TABLE `signalEvaluations` (
	`id` int AUTO_INCREMENT NOT NULL,
	`signalId` int NOT NULL,
	`evaluationWindow` varchar(32) NOT NULL,
	`entryReferencePrice` decimal(18,6) NOT NULL,
	`observedPrice` decimal(18,6),
	`evaluatedAt` timestamp,
	`grossReturn` decimal(12,6),
	`outcome` enum('pending','favorable','unfavorable','flat') NOT NULL DEFAULT 'pending',
	`noLookaheadConfirmed` boolean NOT NULL,
	`methodologyVersion` varchar(32) NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `signalEvaluations_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE INDEX `auditEvents_entity_idx` ON `auditEvents` (`entityType`,`entityId`);--> statement-breakpoint
CREATE INDEX `intelligenceSignals_symbol_cutoff_idx` ON `intelligenceSignals` (`assetSymbol`,`informationCutoffAt`);--> statement-breakpoint
CREATE INDEX `newsItems_publishedAt_idx` ON `newsItems` (`publishedAt`);--> statement-breakpoint
CREATE INDEX `newsSources_userId_idx` ON `newsSources` (`userId`);--> statement-breakpoint
CREATE INDEX `paperOrders_account_submitted_idx` ON `paperOrders` (`accountId`,`submittedAt`);--> statement-breakpoint
CREATE INDEX `signalEvaluations_signal_idx` ON `signalEvaluations` (`signalId`);