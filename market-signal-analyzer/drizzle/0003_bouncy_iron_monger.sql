DROP INDEX `tradeLearningRecords_account_eval_idx` ON `tradeLearningRecords`;--> statement-breakpoint
ALTER TABLE `tradeLearningRecords` ADD `userId` int NOT NULL;--> statement-breakpoint
CREATE INDEX `tradeLearningRecords_user_eval_idx` ON `tradeLearningRecords` (`userId`,`evaluatedAt`);