# AICL Examples

Practical examples showing how to use AICL with external codebases.

---

## Quick Test: Analyze AICL Itself

Simplest example - use AICL to analyze its own code:

```bash
cd tofu-aicl

docker-compose run --rm tofu-aicl-test \
  python3 run.py experiments/examples/analyze-external-demo.aicl \
  -var="target_path=src/aicl" \
  -var="project_name=AICL Framework"
```

**Expected output:**
```
✅ Successfully loaded external codebase for analysis
Project: AICL Framework
Path: src/aicl
```

---

## Analyze Another Project

**Example: Analyze a different codebase on your machine**

```bash
# Method 1: Mount via Docker
docker-compose run --rm \
  -v /path/to/other/project:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py experiments/examples/analyze-external-demo.aicl \
  -var="target_path=/mnt/external" \
  -var="project_name=My Other Project"

# Method 2: Use existing mount point
docker-compose run --rm \
  -v ~/my-react-app:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py experiments/examples/analyze-external-demo.aicl \
  -var="project_name=My React App"
```

---

## Real Examples

### Example 1: Analyze Open Source Project

```bash
# 1. Clone it
git clone https://github.com/pallets/flask /tmp/flask

# 2. Analyze it
docker-compose run --rm \
  -v /tmp/flask:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py experiments/examples/analyze-external-demo.aicl \
  -var="project_name=Flask Framework"
```

### Example 2: Analyze Work Project

```bash
docker-compose run --rm \
  -v ~/work/my-api:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py experiments/examples/analyze-external-demo.aicl \
  -var="target_path=/mnt/external/src" \
  -var="project_name=Work API"
```

### Example 3: Compare Projects

```bash
# Analyze Project A
docker-compose run --rm \
  -v ~/projectA:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py experiments/examples/analyze-external-demo.aicl \
  -var="project_name=Project A" \
  > analysis-a.txt

# Analyze Project B
docker-compose run --rm \
  -v ~/projectB:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py experiments/examples/analyze-external-demo.aicl \
  -var="project_name=Project B" \
  > analysis-b.txt

# Compare results
diff analysis-a.txt analysis-b.txt
```

---

## Configuration Examples

### Via CLI Variables (Recommended)

```bash
./aicl_modular run experiments/examples/analyze-external-demo.aicl \
  -var="target_path=/custom/path" \
  -var="project_name=Custom Project"
```

### Via Environment Variables

```bash
export AICL_TARGET_PATH="/mnt/external"
export AICL_PROJECT_NAME="My Project"

./aicl_modular run experiments/examples/analyze-external-demo.aicl
```

### Via Config File

**Create:** `my-config.yaml`

```yaml
variables:
  target_path: "/mnt/external"
  project_name: "My Project"
```

**Use:**

```bash
./aicl_modular run experiments/examples/analyze-external-demo.aicl \
  --config my-config.yaml
```

---

## Tips

1. **Always mount as read-only** (`:ro`)
2. **Use absolute paths** in Docker
3. **Test with AICL itself first**
4. **Then try external projects**

---

## Next Steps

1. ✅ Try the demo with AICL's own code
2. ✅ Mount an external project
3. ✅ Modify the experiment for your needs
4. ✅ Create your own experiments

See: 
- `/docs/EXPERIMENT_BUILDER_GUIDE.md` - Complete guide
- `/docs/QUICK_START_EXTERNAL.md` - Quick reference
