#!/usr/bin/env python3
"""
Get Fiona M Watt's actual publications using the working query format.
"""

import asyncio
import httpx
import json

async def get_fiona_publications():
    """Get Fiona M Watt's actual publications."""
    
    print("🎯 Getting Fiona M Watt's actual publications")
    print("=" * 60)
    
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Use the working query format
        print("\n📚 Fiona M Watt publications (AUTH:Watt AND Fiona)")
        try:
            params = {
                "query": "AUTH:Watt AND Fiona",
                "resultType": "lite",
                "pageSize": 20,
                "format": "json",
                "sort": "date"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"Found: {result.get('hitCount', 0)} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                fiona_watt_papers = []
                
                for pub in result['resultList']['result']:
                    # Check if this is actually Fiona M Watt
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            author_list = authors
                        else:
                            author_list = [authors]
                        
                        # Look for Fiona M Watt specifically
                        is_fiona_watt = False
                        fiona_author = None
                        
                        for author in author_list:
                            if isinstance(author, dict):
                                full_name = author.get('fullName', '').lower()
                                if ('fiona' in full_name and 'watt' in full_name) or \
                                   ('f' in full_name and 'm' in full_name and 'watt' in full_name) or \
                                   ('fm' in full_name and 'watt' in full_name):
                                    is_fiona_watt = True
                                    fiona_author = author
                                    break
                        
                        if is_fiona_watt:
                            fiona_watt_papers.append({
                                'publication': pub,
                                'fiona_author': fiona_author
                            })
                
                print(f"\n🎯 Filtered to Fiona M Watt specifically: {len(fiona_watt_papers)} publications")
                
                # Show recent papers
                recent_papers = sorted(fiona_watt_papers, 
                                     key=lambda x: x['publication'].get('firstPublicationDate', ''), 
                                     reverse=True)[:10]
                
                print("\n📖 Recent Fiona M Watt Publications:")
                for i, paper_info in enumerate(recent_papers):
                    pub = paper_info['publication']
                    fiona_author = paper_info['fiona_author']
                    
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    journal = pub.get('journalInfo', {}).get('journal', {}).get('title', 'Unknown journal')
                    
                    print(f"\n{i+1}. {title}")
                    print(f"   Journal: {journal} ({date})")
                    print(f"   Fiona's name in paper: {fiona_author.get('fullName', 'Unknown')}")
                    
                    # Check affiliation
                    affiliation = fiona_author.get('affiliation', '')
                    if affiliation:
                        print(f"   Affiliation: {affiliation}")
                        if 'EMBO' in affiliation or 'embo' in affiliation.lower():
                            print("   🎯 EMBO DIRECTOR FOUND!")
                        elif 'King' in affiliation and 'College' in affiliation:
                            print("   🏛️ King's College London")
                    
                    # Show all authors
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            author_names = [a.get('fullName', 'Unknown') for a in authors[:5]]
                        else:
                            author_names = [authors.get('fullName', 'Unknown')]
                        print(f"   Authors: {', '.join(author_names)}")
                        if len(authors) > 5:
                            print(f"   ... and {len(authors) - 5} more authors")
                
                # Look specifically for EMBO-affiliated papers
                print("\n🏢 EMBO-affiliated papers:")
                embo_papers = []
                for paper_info in fiona_watt_papers:
                    fiona_author = paper_info['fiona_author']
                    affiliation = fiona_author.get('affiliation', '').lower()
                    if 'embo' in affiliation:
                        embo_papers.append(paper_info)
                
                if embo_papers:
                    print(f"Found {len(embo_papers)} EMBO-affiliated papers:")
                    for paper_info in embo_papers[:5]:
                        pub = paper_info['publication']
                        title = pub.get('title', 'No title')[:80]
                        date = pub.get('firstPublicationDate', 'No date')
                        print(f"   • {title}... ({date})")
                else:
                    print("No EMBO-affiliated papers found in this set")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_fiona_publications())
