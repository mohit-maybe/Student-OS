import {
  boolean,
  decimal,
  index,
  int,
  json,
  mysqlEnum,
  mysqlTable,
  text,
  timestamp,
  uniqueIndex,
  varchar,
} from "drizzle-orm/mysql-core";

export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export const newsSources = mysqlTable(
  "newsSources",
  {
    id: int("id").autoincrement().primaryKey(),
    userId: int("userId"),
    provider: varchar("provider", { length: 64 }).notNull(),
    displayName: varchar("displayName", { length: 160 }).notNull(),
    kind: mysqlEnum("kind", ["gdelt", "rss", "api"]).notNull(),
    baseUrl: varchar("baseUrl", { length: 2048 }).notNull(),
    connectionStatus: mysqlEnum("connectionStatus", ["connected", "attention", "unconfigured"])
      .default("unconfigured")
      .notNull(),
    enabled: boolean("enabled").default(true).notNull(),
    lastFetchedAt: timestamp("lastFetchedAt"),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  table => [index("newsSources_userId_idx").on(table.userId)]
);

export const newsItems = mysqlTable(
  "newsItems",
  {
    id: int("id").autoincrement().primaryKey(),
    sourceId: int("sourceId"),
    providerItemId: varchar("providerItemId", { length: 512 }).notNull(),
    canonicalUrl: varchar("canonicalUrl", { length: 2048 }).notNull(),
    title: text("title").notNull(),
    summary: text("summary"),
    author: varchar("author", { length: 255 }),
    publisher: varchar("publisher", { length: 255 }),
    publisherUrl: varchar("publisherUrl", { length: 2048 }),
    imageUrl: varchar("imageUrl", { length: 2048 }),
    language: varchar("language", { length: 32 }),
    publishedAt: timestamp("publishedAt"),
    acquiredAt: timestamp("acquiredAt").defaultNow().notNull(),
    contentFingerprint: varchar("contentFingerprint", { length: 128 }).notNull(),
    rawPayload: json("rawPayload"),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  table => [
    uniqueIndex("newsItems_provider_fingerprint_unique").on(table.providerItemId, table.contentFingerprint),
    index("newsItems_publishedAt_idx").on(table.publishedAt),
  ]
);

export const intelligenceSignals = mysqlTable(
  "intelligenceSignals",
  {
    id: int("id").autoincrement().primaryKey(),
    newsItemId: int("newsItemId").notNull(),
    assetSymbol: varchar("assetSymbol", { length: 32 }).notNull(),
    assetClass: mysqlEnum("assetClass", ["equity", "crypto", "etf", "macro"]).notNull(),
    catalyst: varchar("catalyst", { length: 96 }).notNull(),
    direction: mysqlEnum("direction", ["upside", "downside", "mixed", "watch"]).notNull(),
    sentiment: mysqlEnum("sentiment", ["positive", "negative", "neutral", "mixed"]).notNull(),
    confidence: int("confidence").notNull(),
    hypothesis: text("hypothesis").notNull(),
    uncertainty: text("uncertainty").notNull(),
    evidenceExcerpt: text("evidenceExcerpt").notNull(),
    informationCutoffAt: timestamp("informationCutoffAt").notNull(),
    modelName: varchar("modelName", { length: 96 }).notNull(),
    promptVersion: varchar("promptVersion", { length: 32 }).notNull(),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  table => [index("intelligenceSignals_symbol_cutoff_idx").on(table.assetSymbol, table.informationCutoffAt)]
);

export const paperAccounts = mysqlTable(
  "paperAccounts",
  {
    id: int("id").autoincrement().primaryKey(),
    userId: int("userId").notNull(),
    baseCurrency: varchar("baseCurrency", { length: 8 }).default("USD").notNull(),
    virtualCash: decimal("virtualCash", { precision: 18, scale: 2 }).notNull(),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  table => [uniqueIndex("paperAccounts_user_unique").on(table.userId)]
);

export const paperOrders = mysqlTable(
  "paperOrders",
  {
    id: int("id").autoincrement().primaryKey(),
    accountId: int("accountId").notNull(),
    signalId: int("signalId"),
    symbol: varchar("symbol", { length: 32 }).notNull(),
    assetClass: mysqlEnum("assetClass", ["equity", "crypto", "etf"]).notNull(),
    side: mysqlEnum("side", ["buy", "sell"]).notNull(),
    quantity: decimal("quantity", { precision: 18, scale: 6 }).notNull(),
    requestedPrice: decimal("requestedPrice", { precision: 18, scale: 6 }).notNull(),
    fillPrice: decimal("fillPrice", { precision: 18, scale: 6 }),
    status: mysqlEnum("status", ["queued", "filled", "cancelled", "rejected"]).default("queued").notNull(),
    rationale: text("rationale").notNull(),
    informationCutoffAt: timestamp("informationCutoffAt").notNull(),
    submittedAt: timestamp("submittedAt").defaultNow().notNull(),
    filledAt: timestamp("filledAt"),
  },
  table => [index("paperOrders_account_submitted_idx").on(table.accountId, table.submittedAt)]
);

export const paperPositions = mysqlTable(
  "paperPositions",
  {
    id: int("id").autoincrement().primaryKey(),
    accountId: int("accountId").notNull(),
    symbol: varchar("symbol", { length: 32 }).notNull(),
    assetClass: mysqlEnum("assetClass", ["equity", "crypto", "etf"]).notNull(),
    quantity: decimal("quantity", { precision: 18, scale: 6 }).notNull(),
    averagePrice: decimal("averagePrice", { precision: 18, scale: 6 }).notNull(),
    markPrice: decimal("markPrice", { precision: 18, scale: 6 }).notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  table => [uniqueIndex("paperPositions_account_symbol_unique").on(table.accountId, table.symbol)]
);

export const signalEvaluations = mysqlTable(
  "signalEvaluations",
  {
    id: int("id").autoincrement().primaryKey(),
    signalId: int("signalId").notNull(),
    evaluationWindow: varchar("evaluationWindow", { length: 32 }).notNull(),
    entryReferencePrice: decimal("entryReferencePrice", { precision: 18, scale: 6 }).notNull(),
    observedPrice: decimal("observedPrice", { precision: 18, scale: 6 }),
    evaluatedAt: timestamp("evaluatedAt"),
    grossReturn: decimal("grossReturn", { precision: 12, scale: 6 }),
    outcome: mysqlEnum("outcome", ["pending", "favorable", "unfavorable", "flat"]).default("pending").notNull(),
    noLookaheadConfirmed: boolean("noLookaheadConfirmed").notNull(),
    methodologyVersion: varchar("methodologyVersion", { length: 32 }).notNull(),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  table => [index("signalEvaluations_signal_idx").on(table.signalId)]
);

export const auditEvents = mysqlTable(
  "auditEvents",
  {
    id: int("id").autoincrement().primaryKey(),
    userId: int("userId"),
    eventType: varchar("eventType", { length: 96 }).notNull(),
    entityType: varchar("entityType", { length: 96 }).notNull(),
    entityId: varchar("entityId", { length: 96 }).notNull(),
    details: json("details"),
    occurredAt: timestamp("occurredAt").defaultNow().notNull(),
  },
  table => [index("auditEvents_entity_idx").on(table.entityType, table.entityId)]
);

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;
