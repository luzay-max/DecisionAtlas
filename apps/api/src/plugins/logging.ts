export type LogMeta = {
  workspace_id?: number;
  job_id?: string;
  artifact_id?: number;
};

export function createLogMeta(meta: LogMeta): LogMeta {
  return Object.fromEntries(Object.entries(meta).filter(([, value]) => value !== undefined)) as LogMeta;
}

export function logInfo(
  logger: { info: (meta: Record<string, unknown>, message: string) => void },
  message: string,
  meta: LogMeta
) {
  logger.info(createLogMeta(meta), message);
}
