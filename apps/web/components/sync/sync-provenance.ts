import type { Messages } from "../i18n/messages";

export function syncOriginLabel(messages: Messages, origin: string | null | undefined): string | null {
  if (!origin) {
    return null;
  }
  return messages.status[origin as keyof typeof messages.status] ?? origin;
}

export function syncEventLabel(messages: Messages, event: string | null | undefined): string | null {
  if (!event) {
    return null;
  }
  return messages.syncEvents[event as keyof typeof messages.syncEvents] ?? event;
}

export function syncSummary(
  messages: Messages,
  sync: {
    sync_origin?: string | null;
    trigger_event?: string | null;
    mode?: string | null;
    status?: string | null;
  } | null | undefined
): string | null {
  if (!sync) {
    return null;
  }
  const origin = syncOriginLabel(messages, sync.sync_origin) ?? sync.mode ?? null;
  if (!origin) {
    return null;
  }
  const triggerEvent = syncEventLabel(messages, sync.trigger_event);
  const status = sync.status ? (messages.status[sync.status as keyof typeof messages.status] ?? sync.status) : null;
  return [origin, triggerEvent, status].filter(Boolean).join(" · ");
}
