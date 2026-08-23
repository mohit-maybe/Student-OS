import { desc, eq } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, newsItems, users } from "../drizzle/schema";
import type { NormalizedNewsItem } from "./marketCore";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

export async function retainNewsItems(items: NormalizedNewsItem[]) {
  const db = await getDb();
  if (!db || items.length === 0) return { retained: 0, unavailable: !db };

  const values = items.map(item => ({
    providerItemId: item.providerItemId,
    canonicalUrl: item.canonicalUrl,
    title: item.title,
    summary: item.summary,
    publisher: item.publisher,
    publisherUrl: item.publisherUrl,
    imageUrl: item.imageUrl,
    language: item.language,
    publishedAt: item.publishedAt,
    acquiredAt: item.acquiredAt,
    contentFingerprint: item.contentFingerprint,
    rawPayload: item.rawPayload,
  }));

  await db.insert(newsItems).values(values).onDuplicateKeyUpdate({
    set: { acquiredAt: new Date() },
  });
  return { retained: values.length, unavailable: false };
}

export async function listRetainedNews(limit = 12) {
  const db = await getDb();
  if (!db) return [];
  return db.select({
    id: newsItems.id,
    title: newsItems.title,
    canonicalUrl: newsItems.canonicalUrl,
    publisher: newsItems.publisher,
    publishedAt: newsItems.publishedAt,
    acquiredAt: newsItems.acquiredAt,
    contentFingerprint: newsItems.contentFingerprint,
  }).from(newsItems).orderBy(desc(newsItems.acquiredAt)).limit(limit);
}

// TODO: add feature queries here as your product grows.
