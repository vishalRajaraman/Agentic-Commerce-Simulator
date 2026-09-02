import re

with open('seed_massive_catalog.py', 'r') as f:
    content = f.read()

# Extract products_data list using regex
match = re.search(r'products_data\s*=\s*(\[.*?\])\n\nprint', content, re.DOTALL)
if match:
    import ast
    products = ast.literal_eval(match.group(1))
    
    new_products = []
    for p in products:
        new_products.append(p)
        
        alt_p = dict(p)
        alt_p['product_id'] = p['product_id'] + '_alt'
        
        # change merchant slightly
        merchant_num = int(re.search(r'\d+', p['merchant_id']).group())
        alt_merchant_num = (merchant_num % 7) + 1
        alt_p['merchant_id'] = re.sub(r'\d+', f"{alt_merchant_num:03d}", p['merchant_id'])
        if alt_p['merchant_id'] == p['merchant_id']:
            alt_merchant_num = (merchant_num + 1) % 7 + 1
            alt_p['merchant_id'] = re.sub(r'\d+', f"{alt_merchant_num:03d}", p['merchant_id'])
            
        alt_p['base_price'] = round(p['base_price'] * 0.9, 2)
        alt_p['description'] = p['description'] + ' (Alt)'
        alt_p['bundle_rules'] = 'No bundle rules'
        
        new_products.append(alt_p)
    
    # Write back the new products_data
    import json
    new_products_str = "products_data = " + json.dumps(new_products, indent=4)
    new_content = content[:match.start()] + new_products_str + "\n\nprint" + content[match.end():]
    
    with open('seed_massive_catalog.py', 'w') as f:
        f.write(new_content)
    print("Updated seed_massive_catalog.py successfully.")
else:
    print("Could not parse products_data.")
