import random
import uuid

class MockMerchantAgent:
    def __init__(self, merchant_id: str, category: str):
        self.merchant_id = merchant_id
        self.category = category
        
        # Base prices depend on category
        if "electronics" in category:
            self.base_price = random.randint(300, 1000)
        elif "clothing" in category:
            self.base_price = random.randint(20, 100)
        else:
            self.base_price = random.randint(10, 50)
            
        self.floor_price = int(self.base_price * 0.8) # Will not go below 80%

    def process_rfq(self, item_description: str) -> dict:
        """
        Handle the initial RFQ from the Buyer Agent.
        """
        return {
            "merchant_id": self.merchant_id,
            "status": "quote_offered",
            "quoted_price": self.base_price,
            "message": f"We have '{item_description}' in stock. Our initial price is ${self.base_price}."
        }
        
    def negotiate(self, proposed_price: float) -> dict:
        """
        Handle a counter-offer from the Buyer Agent.
        """
        if proposed_price >= self.base_price:
            return {"status": "accepted", "final_price": proposed_price, "message": "Deal! We accept your offer."}
        
        if proposed_price >= self.floor_price:
            # Maybe accept, or maybe counter somewhere in between
            if random.random() > 0.5:
                return {"status": "accepted", "final_price": proposed_price, "message": "You drive a hard bargain, but we accept."}
            else:
                counter = int((proposed_price + self.base_price) / 2)
                self.base_price = counter # Lower our internal base price expectation
                return {"status": "counter_offer", "quoted_price": counter, "message": f"We can't do ${proposed_price}, but we can meet at ${counter}."}
        
        return {"status": "rejected", "message": f"Sorry, ${proposed_price} is too low. Our absolute best is ${self.floor_price}."}

    def generate_razorpay_link(self, final_price: float) -> str:
        """
        Simulate generating a Razorpay payment link after deal is finalized.
        """
        mock_payment_id = uuid.uuid4().hex[:8]
        return f"https://rzp.io/i/{mock_payment_id}?amount={final_price}"

# Global registry of mock merchants for testing
ACTIVE_MOCK_MERCHANTS = {}

def get_merchant_agent(merchant_id: str, category: str = "general") -> MockMerchantAgent:
    if merchant_id not in ACTIVE_MOCK_MERCHANTS:
        ACTIVE_MOCK_MERCHANTS[merchant_id] = MockMerchantAgent(merchant_id, category)
    return ACTIVE_MOCK_MERCHANTS[merchant_id]
