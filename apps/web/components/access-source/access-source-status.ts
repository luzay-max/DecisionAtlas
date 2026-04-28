import type { Messages } from "../i18n/messages";

export function accessSourceStatusLabel(messages: Messages, status: string | null | undefined): string | null {
  if (!status) {
    return null;
  }
  return messages.status[status as keyof typeof messages.status] ?? status;
}

export function privateAccessRecoveryCopy(messages: Messages, status: string | null | undefined): string | null {
  if (!status) {
    return null;
  }
  return messages.privateAccess.recovery[status as keyof typeof messages.privateAccess.recovery] ?? null;
}

export function accessRequirementCopy(messages: Messages, requirement: string | null | undefined): string | null {
  if (!requirement) {
    return null;
  }
  return messages.liveAnalysis.accessRequirements[requirement as keyof typeof messages.liveAnalysis.accessRequirements] ?? null;
}
