# Test Code Extraction

This file demonstrates various code block patterns.

## Explicit Filename - New File

```python
# New file: src/data_processor.py
class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self, items):
        return [item.upper() for item in items]
```

## Explicit Filename - Modification

```python
# In utils.py
def helper_function(x, y):
    return x + y
```

## Auto-Generated - Class Name

```python
class UserAuthenticationService:
    def authenticate(self, username, password):
        # Check credentials
        return True
```

## Auto-Generated - Function Name

```python
def calculate_metrics(data):
    total = sum(data)
    average = total / len(data)
    return {'total': total, 'average': average}
```

## Auto-Generated - Pattern Detection (Test)

```python
import unittest

class TestDataProcessor(unittest.TestCase):
    def test_processing(self):
        processor = DataProcessor()
        result = processor.process(['a', 'b'])
        self.assertEqual(result, ['A', 'B'])
```

## Auto-Generated - Pattern Detection (API)

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    return jsonify({'data': [1, 2, 3]})
```

## JavaScript with Explicit Name

```javascript
// New file: components/Button.jsx
import React from 'react';

export default function Button({ label, onClick }) {
  return <button onClick={onClick}>{label}</button>;
}
```

## JavaScript Auto-Generated

```javascript
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

module.exports = { calculateTotal };
```

## Shell Script

```bash
# New file: scripts/deploy.sh
#!/bin/bash
echo "Deploying application..."
npm run build
npm run deploy
```

## Configuration File

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

