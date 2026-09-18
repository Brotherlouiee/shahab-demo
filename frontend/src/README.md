# Target frontend source structure

`app/` is the composition root; `shared/` contains only dependency-free cross-feature code; each `features/` directory owns one product capability. Presentation code may depend on application contracts but not raw source documents, database code, or scoring formulas.
