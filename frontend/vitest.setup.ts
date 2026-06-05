import "@testing-library/jest-dom";
import { server } from "./src/mocks/server";

// Start MSW server before all tests, reset handlers after each test,
// stop the server once all tests are done.
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
