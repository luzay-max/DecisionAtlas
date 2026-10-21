import { buildServer } from "../src/server";

it("forwards the original webhook bytes without JSON normalization", async () => {
  const previous = global.fetch;
  const requestBody = '{ "action" : "opened" }\n';
  global.fetch = vi.fn().mockResolvedValue({
    status: 200,
    ok: true,
    text: async () => JSON.stringify({ status: "ignored" }),
  } as Response);
  try {
    const app = buildServer();
    const result = await app.inject({
      method: "POST",
      url: "/imports/github/webhook",
      headers: { "content-type": "application/json", "x-github-event": "pull_request" },
      payload: requestBody,
    });
    expect(result.statusCode).toBe(200);
    const sent = (global.fetch as any).mock.calls[0][1];
    expect(Buffer.from(sent.body).toString()).toBe(requestBody);
    await app.close();
  } finally {
    global.fetch = previous;
  }
});
