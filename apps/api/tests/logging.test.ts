import { createLogMeta, logInfo } from "../src/plugins/logging";

describe("logging plugin", () => {
  it("builds structured metadata without undefined fields", () => {
    expect(createLogMeta({ workspace_id: 7, job_id: "job-123", artifact_id: undefined })).toEqual({
      workspace_id: 7,
      job_id: "job-123"
    });
  });

  it("passes structured metadata to the logger", () => {
    const logger = {
      info: vi.fn()
    };

    logInfo(logger, "import started", { workspace_id: 9, job_id: "job-456", artifact_id: 12 });

    expect(logger.info).toHaveBeenCalledWith(
      { workspace_id: 9, job_id: "job-456", artifact_id: 12 },
      "import started"
    );
  });
});
