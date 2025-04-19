from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

load_dotenv()

def generate_diplomacy_orders(game, power_name, possible_orders, llm, agent):
    """
    Generate orders for a Diplomacy power using LangChain and Claude.
    
    Args:
        game: The current game state
        power_name (str): Name of the power (e.g., 'FRANCE')
        possible_orders (dict): Dictionary of possible orders for each location
        llm: The language model instance
        agent: The agent with memory of previous interactions
        
    Returns:
        list[str]: List of orders in Diplomacy format
    """
    
    # Get chat history from agent
    memory_vars = agent.memory.load_memory_variables({})
    chat_history = memory_vars.get('chat_history', '')
    
    # Create prompt template
    prompt_template = PromptTemplate(
        input_variables=["power_name", "game_state", "possible_orders", "chat_history"],
        template=open("/Users/jialingjiao/Library/CloudStorage/OneDrive-TheUniversityofChicago/AI/playground/LLM_Diplomacy/Diplomacy_Prompt").read()
    )
    
    # Create the chain
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    # Prepare input
    chain_input = {
        "power_name": power_name,
        "game_state": game.get_state(),
        "possible_orders": possible_orders,
        "chat_history": chat_history
    }
    
    # Run the chain
    result = chain.invoke(chain_input)
    response = result['text']
    
    # Extract orders (lines starting with A or F) or negotiations
    orders = []
    negotiations = []
    
    for line in response.split('\n'):
        line = line.strip()
        if line.startswith(('A ', 'F ')):
            orders.append(line)
        elif line.startswith('NEGOTIATE '):
            negotiations.append(line)
    
    # Save the orders to agent's memory
    agent.memory.save_context(
        {"input": f"Orders for {power_name}"},
        {"output": "\n".join(orders)}
    )
    
    return orders, negotiations

def negotiate_between_agents(initiator_agent, target_agent, initiator_llm, target_llm, initiator_power, target_power, game_state, game, possible_orders):
    """
    Simulate a negotiation between two Diplomacy powers using their agents' memories.
    The agents can either continue negotiating or submit orders.
    
    Args:
        initiator_agent: The agent for the power initiating the negotiation
        target_agent: The agent for the power being negotiated with
        initiator_llm: The LLM for the initiator
        target_llm: The LLM for the target
        initiator_power (str): Name of the power initiating the negotiation
        target_power (str): Name of the power being negotiated with
        game_state: Current state of the game
        game: The current game instance
        possible_orders: Dictionary of possible orders for each location
        
    Returns:
        tuple: (initiator_message, target_response, orders) where orders is None if negotiation continues
    """
    # Create negotiation prompt template
    negotiation_prompt = PromptTemplate(
        input_variables=["input", "initiator_power", "target_power", "game_state", "chat_history"],
        template=open("Negotiation_Prompt").read()
    )
    
    # Create response prompt template
    response_prompt = PromptTemplate(
        input_variables=["input", "initiator_power", "target_power", "game_state", "message", "chat_history"],
        template=open("Negotiation_Response_Prompt").read()
    )
    
    # Get chat history from memory
    initiator_memory = initiator_agent.memory.load_memory_variables({})
    target_memory = target_agent.memory.load_memory_variables({})
    
    # Create chains with memory
    negotiation_chain = LLMChain(
        llm=initiator_llm,
        prompt=negotiation_prompt,
        memory=initiator_agent.memory,
        output_key="output"
    )
    
    response_chain = LLMChain(
        llm=target_llm,
        prompt=response_prompt,
        memory=target_agent.memory,
        output_key="output"
    )
    
    # Generate initial message
    initiator_input = {
        "input": f"{initiator_power} to {target_power}",
        "initiator_power": initiator_power,
        "target_power": target_power,
        "game_state": game_state,
        "chat_history": initiator_memory.get('chat_history', '')
    }
    initiator_result = negotiation_chain.invoke(initiator_input)
    initiator_message = initiator_result['output']
    
    # Check if initiator wants to submit orders
    if "I'm ready to submit an order" in initiator_message:
        orders, _ = generate_diplomacy_orders(game, initiator_power, possible_orders, initiator_llm, initiator_agent)
        return initiator_message, None, orders
    
    # Save initiator's message to both memories
    initiator_agent.memory.save_context(
        {"input": f"{initiator_power} to {target_power}"},
        {"output": initiator_message}
    )
    target_agent.memory.save_context(
        {"input": f"Message from {initiator_power}"},
        {"output": initiator_message}
    )
    
    # Generate response
    target_input = {
        "input": f"{target_power} to {initiator_power}",
        "initiator_power": initiator_power,
        "target_power": target_power,
        "game_state": game_state,
        "message": initiator_message,
        "chat_history": target_memory.get('chat_history', '')
    }
    target_result = response_chain.invoke(target_input)
    target_response = target_result['output']
    
    # Check if target wants to submit orders
    if "I'm ready to submit an order" in target_response:
        orders, _ = generate_diplomacy_orders(game, target_power, possible_orders, target_llm, target_agent)
        return initiator_message, target_response, orders
    
    # Save target's response to both memories
    initiator_agent.memory.save_context(
        {"input": f"Response from {target_power}"},
        {"output": target_response}
    )
    target_agent.memory.save_context(
        {"input": f"{target_power} to {initiator_power}"},
        {"output": target_response}
    )
    
    return initiator_message, target_response, None

def create_diplomacy_agent(power_name):
    """Create a more sophisticated Diplomacy agent using LangChain"""
    llm = ChatAnthropic(model=os.getenv('ANTHROPIC_MODEL'), anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Simple memory that just stores all messages
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="input",
        output_key="output"
    )
    
    # Create a tool that uses the LLM
    def analyze_game_state(query):
        return llm.invoke(query)
    
    # Create tools the agent can use
    tools = [
        Tool(
            name="analyze_game_state",
            func=analyze_game_state,
            description="Analyzes the current game state and provides strategic insights"
        )
    ]
    
    # Initialize the agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )
    
    return agent, llm 