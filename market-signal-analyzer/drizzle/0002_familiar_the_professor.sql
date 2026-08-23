CREATE TABLE `tradeLearningRecords` (
	`id` int AUTO_INCREMENT NOT NULL,
	`accountId` int,
	`orderId` int,
	`signalId` int,
	`symbol` varchar(32) NOT NULL,
	`side` enum('long','short') NOT NULL,
	`entryPrice` decimal(18,6) NOT NULL,
	`exitPrice` decimal(18,6) NOT NULL,
	`quantity` decimal(18,6) NOT NULL,
	`fees` decimal(18,6) NOT NULL,
	`grossPnl` decimal(18,6) NOT NULL,
	`netPnl` decimal(18,6) NOT NULL,
	`outcome` enum('win','loss','flat') NOT NULL,
	`decisionAt` timestamp NOT NULL,
	`evaluatedAt` timestamp NOT NULL,
	`sourceUrls` json NOT NULL,
	`rationale` text NOT NULL,
	`errorCategory` varchar(64) NOT NULL,
	`lesson` text NOT NULL,
	`learningStatus` enum('pending_human_review','approved','rejected') NOT NULL DEFAULT 'pending_human_review',
	`modelVersion` varchar(96) NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `tradeLearningRecords_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE INDEX `tradeLearningRecords_account_eval_idx` ON `tradeLearningRecords` (`accountId`,`evaluatedAt`);