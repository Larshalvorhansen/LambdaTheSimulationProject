```markdown
# Approaches - Experimental Implementations

This is a collection of experimental approaches and small-scale tests for the Lambda Simulation Project. Each folder represents a unique approach or concept that is tested independently of the main project.

## 📁 Structure

Each folder in `approaches/` is a self-contained mini-project with its own implementation:

```
approaches/
├── approach_name_1/
│   ├── version1.py
│   ├── version2.py
│   └── ...
├── approach_name_2/
│   ├── version1.py
│   └── ...
└── ...
```

## 🔬 Purpose

This folder is used to:
- **Test new concepts** - Explore alternative implementations before integrating them into the main project
- **Compare approaches** - Evaluate different methods side-by-side
- **Rapid prototyping** - Experiment without affecting the main codebase
- **Version control** - Keep track of iterations (version1.py, version2.py, etc.)

## 🚀 How to Run

Each mini-project runs independently:

```bash
cd approaches/approach_name
python version1.py
```

To test a specific version:

```bash
python version2.py
```

## 📊 Evaluation

When an approach shows promising results:
1. It is thoroughly documented
2. Results are compared with other approaches
3. The best solution is considered for integration into the main project

## 🔄 Relation to Main Project

Successful experiments from here can become the foundation for components in the main project's pipeline, especially in:
- Simulation phase
- Node/relation structuring
- Processing algorithms

---

*For the main project's structure and overall overview, see [README.md](../README.md) in the root folder.*
```
