# EuropePMC CLI Search Commands

## Basic Search Commands

### 1. Simple Author Search
```bash
# Search for papers by author surname
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=Watt&format=json&pageSize=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Found: {data.get(\"hitCount\", 0):,} papers')
for i, pub in enumerate(data.get('resultList', {}).get('result', [])[:5]):
    print(f'{i+1}. {pub.get(\"title\", \"No title\")}')
    print(f'   Authors: {pub.get(\"authorString\", \"No authors\")}')
    print(f'   Journal: {pub.get(\"journalTitle\", \"No journal\")} ({pub.get(\"firstPublicationDate\", \"No date\")})')
    print()
"
```

### 2. Search with Author Filtering
```bash
# Search for Watt papers and filter for Fiona
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=Watt&format=json&pageSize=50" | python3 -c "
import sys, json
data = json.load(sys.stdin)
publications = data.get('resultList', {}).get('result', [])
print(f'Searching through {len(publications)} Watt papers for Fiona...')

fiona_papers = []
for pub in publications:
    authors = pub.get('authorString', '').lower()
    if any(name in authors for name in ['fiona', 'f watt', 'watt f']):
        fiona_papers.append(pub)

print(f'Found {len(fiona_papers)} potential Fiona Watt papers!')
for i, paper in enumerate(fiona_papers[:5]):
    print(f'{i+1}. {paper.get(\"title\", \"No title\")}')
    print(f'   Authors: {paper.get(\"authorString\", \"No authors\")}')
    print(f'   PMID: {paper.get(\"pmid\", \"No PMID\")}')
    print()
"
```

### 3. Topic-Based Search
```bash
# Search for stem cell papers
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=stem%20cell&format=json&pageSize=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Found: {data.get(\"hitCount\", 0):,} stem cell papers')
for i, pub in enumerate(data.get('resultList', {}).get('result', [])[:3]):
    print(f'{i+1}. {pub.get(\"title\", \"No title\")}')
    print(f'   Authors: {pub.get(\"authorString\", \"No authors\")}')
    print()
"
```

### 4. Recent Papers Search
```bash
# Search for recent papers (2020 onwards)
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=Watt%20AND%20FIRST_PDATE:[2020%20TO%20*]&format=json&pageSize=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Found: {data.get(\"hitCount\", 0):,} recent Watt papers (2020+)')
for i, pub in enumerate(data.get('resultList', {}).get('result', [])[:5]):
    print(f'{i+1}. {pub.get(\"title\", \"No title\")}')
    print(f'   Authors: {pub.get(\"authorString\", \"No authors\")}')
    print(f'   Date: {pub.get(\"firstPublicationDate\", \"No date\")}')
    print()
"
```

## Advanced Search Commands

### 5. Search with Institution Context
```bash
# Search for Watt + EMBO
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=Watt%20EMBO&format=json&pageSize=20" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Found: {data.get(\"hitCount\", 0):,} Watt + EMBO papers')
for i, pub in enumerate(data.get('resultList', {}).get('result', [])[:5]):
    print(f'{i+1}. {pub.get(\"title\", \"No title\")}')
    print(f'   Authors: {pub.get(\"authorString\", \"No authors\")}')
    print()
"
```

### 6. Detailed Paper Information
```bash
# Get detailed info for a specific PMID
PMID="12345678"  # Replace with actual PMID
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/MED/${PMID}?format=json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
result = data.get('result', {})
print(f'Title: {result.get(\"title\", \"No title\")}')
print(f'Authors: {result.get(\"authorString\", \"No authors\")}')
print(f'Journal: {result.get(\"journalInfo\", {}).get(\"journal\", {}).get(\"title\", \"No journal\")}')
print(f'Date: {result.get(\"firstPublicationDate\", \"No date\")}')
print(f'Abstract: {result.get(\"abstractText\", \"No abstract\")[:200]}...')
"
```

## Quick One-Liners

### Count Results Only
```bash
# Just get the count
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=Watt&format=json&pageSize=1" | python3 -c "import sys,json; print(f'Results: {json.load(sys.stdin).get(\"hitCount\", 0):,}')"
```

### Search Any Author
```bash
# Replace "AUTHOR_NAME" with any author surname
AUTHOR="Smith"  # Change this
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=${AUTHOR}&format=json&pageSize=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Found: {data.get(\"hitCount\", 0):,} papers for ${AUTHOR}')
for i, pub in enumerate(data.get('resultList', {}).get('result', [])[:3]):
    print(f'{i+1}. {pub.get(\"title\", \"No title\")}')
    print(f'   Authors: {pub.get(\"authorString\", \"No authors\")}')
    print()
"
```

### Search with Multiple Terms
```bash
# Search for author + research field
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=Watt%20stem%20cell&format=json&pageSize=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Found: {data.get(\"hitCount\", 0):,} papers for Watt + stem cell')
for i, pub in enumerate(data.get('resultList', {}).get('result', [])[:3]):
    print(f'{i+1}. {pub.get(\"title\", \"No title\")}')
    print(f'   Authors: {pub.get(\"authorString\", \"No authors\")}')
    print()
"
```

## Interactive Search Script

### Custom Search Function
```bash
# Save this as search_europepmc.sh and make it executable
cat > search_europepmc.sh << 'EOF'
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <search_term> [page_size]"
    echo "Example: $0 'Watt' 20"
    exit 1
fi

QUERY="$1"
PAGE_SIZE="${2:-10}"

echo "🔍 Searching EuropePMC for: $QUERY"
echo "📄 Page size: $PAGE_SIZE"
echo "=" $(printf '=%.0s' {1..50})

curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=$(echo "$QUERY" | sed 's/ /%20/g')&format=json&pageSize=$PAGE_SIZE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
hit_count = data.get('hitCount', 0)
print(f'📊 Total results: {hit_count:,}')
print()

publications = data.get('resultList', {}).get('result', [])
for i, pub in enumerate(publications):
    title = pub.get('title', 'No title')
    authors = pub.get('authorString', 'No authors')
    journal = pub.get('journalTitle', 'No journal')
    date = pub.get('firstPublicationDate', 'No date')
    pmid = pub.get('pmid', 'No PMID')
    
    print(f'{i+1:2d}. {title}')
    print(f'    👥 {authors}')
    print(f'    📖 {journal} ({date})')
    print(f'    🔗 PMID: {pmid}')
    print()
"
EOF

chmod +x search_europepmc.sh
```

### Usage Examples:
```bash
# Make the script executable and use it
./search_europepmc.sh "Watt" 20
./search_europepmc.sh "Fiona Watt" 10
./search_europepmc.sh "stem cell" 15
./search_europepmc.sh "Watt EMBO" 25
```

## Pro Tips

1. **URL Encoding**: Spaces become `%20`, quotes become `%22`
2. **Page Size**: Maximum is 1000, but 50-100 is usually sufficient
3. **Date Filtering**: Use `FIRST_PDATE:[2020 TO *]` for recent papers
4. **Boolean Logic**: Use `AND`, `OR`, `NOT` operators
5. **Field Search**: Use `AUTH:`, `TITLE:`, `JOURNAL:` prefixes

## Test Your Setup
```bash
# Quick test to verify everything works
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=cancer&format=json&pageSize=1" | python3 -c "import sys,json; print('✅ API Working!' if json.load(sys.stdin).get('hitCount', 0) > 0 else '❌ API Issue')"
```

This should output: `✅ API Working!`
