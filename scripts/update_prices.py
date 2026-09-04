import re

def update_catalog():
    with open('scripts/seed_massive_catalog.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Multiply base_price by 80
    def replace_base_price(match):
        price = float(match.group(1))
        return f'"base_price": {price * 80},'
    content = re.sub(r'"base_price":\s*([\d\.]+),', replace_base_price, content)

    # Multiply dollar amounts in bundle_rules
    def replace_dollar(match):
        val = float(match.group(1))
        return f'₹{int(val * 80)}'
    content = re.sub(r'\$(\d+)', replace_dollar, content)

    with open('scripts/seed_massive_catalog.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated seed_massive_catalog.py')

if __name__ == '__main__':
    update_catalog()
