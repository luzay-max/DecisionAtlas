import React from "react";
import { render, screen } from "@testing-library/react";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("renders the project name and MVP concepts", () => {
    render(<HomePage />);

    expect(screen.getByText("DecisionAtlas")).toBeInTheDocument();
    expect(screen.getByText(/engineering decision memory/i)).toBeInTheDocument();
    expect(screen.getByText("Import")).toBeInTheDocument();
    expect(screen.getByText("Decisions")).toBeInTheDocument();
    expect(screen.getByText("Why")).toBeInTheDocument();
    expect(screen.getByText(/run the demo import/i)).toBeInTheDocument();
    expect(screen.getByText(/the public demo workspace is seeded for a stable walkthrough/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open the public demo workspace/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /jump to review/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /jump to why search/i })).toBeInTheDocument();
  });
});
