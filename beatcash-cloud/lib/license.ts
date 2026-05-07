import crypto from "crypto";

const SECRET = process.env.LICENSE_SIGNING_SECRET || "dev-secret-change-me";

/** Génère une clé license du format BC-XXXX-XXXX-XXXX-XXXX (alphanum). */
export function generateLicenseKey(): string {
  const groups = Array.from({ length: 4 }, () =>
    Array.from(crypto.randomBytes(3))
      .map((b) => "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"[b % 32])
      .join(""),
  );
  return `BC-${groups.join("-")}`;
}

/** Signe un payload JSON pour qu'il soit vérifiable hors-ligne par le desktop. */
export function signPayload(payload: object): string {
  const data = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const sig  = crypto.createHmac("sha256", SECRET).update(data).digest("base64url");
  return `${data}.${sig}`;
}

export function verifyPayload<T = unknown>(token: string): T | null {
  const [data, sig] = token.split(".");
  if (!data || !sig) return null;
  const expected = crypto.createHmac("sha256", SECRET).update(data).digest("base64url");
  if (expected !== sig) return null;
  try {
    return JSON.parse(Buffer.from(data, "base64url").toString()) as T;
  } catch {
    return null;
  }
}
