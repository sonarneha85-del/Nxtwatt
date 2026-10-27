
from .data import DEMO_CHARGERS


def emergency_analyzer(battery, range_km, energy_kwh):
    if battery <= 10 or range_km <= 15:
        urgency = "High"
    elif battery <= 25 or range_km <= 40:
        urgency = "Medium"
    else:
        urgency = "Low"

    return {
        "agent": "Agent 1: Emergency Analyzer",
        "urgency": urgency,
        "battery_percent": battery,
        "remaining_range_km": range_km,
        "message": f"Battery is {battery}% with {range_km} km range.",
    }


def home_charger_finder(range_km, connector, energy_kwh):
    matches = []

    for charger in DEMO_CHARGERS:
        connectors = charger.get("connectors", [])

        compatible = (
            connector == "Not sure"
            or connector in connectors
        )

        safe_distance = charger["distance_km"] < range_km
        enough_energy = charger["max_energy_kwh"] >= energy_kwh

        if (
            charger["available"]
            and charger["verified_installation"]
            and compatible
            and safe_distance
            and enough_energy
        ):
            matches.append(charger.copy())

    matches.sort(
        key=lambda charger: (
            charger["distance_km"],
            charger["price_per_kwh"],
        )
    )

    return {
        "agent": "Agent 2: Home Charger Finder",
        "matches": matches,
        "count": len(matches),
        "message": f"Found {len(matches)} matching demo chargers.",
    }


def cost_benefit_advisor(energy_kwh, eligible_chargers):
    options = []

    for charger in eligible_chargers:
        total_cost = round(
            energy_kwh * charger["price_per_kwh"], 2
        )

        options.append({
            "charger_id": charger["id"],
            "host": charger["name"],
            "price_per_kwh": charger["price_per_kwh"],
            "total_cost": total_cost,
            "estimated_host_earnings": total_cost,
        })

    return {
        "agent": "Agent 3: Cost-Benefit Advisor",
        "options": options,
        "message": "Compared estimated charging costs.",
    }


def recommendation_agent(emergency, finder, cost):
    if not finder["matches"]:
        return {
            "agent": "Agent 4: Recommendation Agent",
            "selected": None,
            "message": (
                "No suitable demo charger found. "
                "Do not rely on this prototype in an emergency."
            ),
        }

    chargers = finder["matches"]

    max_distance = max(c["distance_km"] for c in chargers)
    max_price = max(c["price_per_kwh"] for c in chargers)

    def score(charger):
        distance_score = (
            charger["distance_km"] / max_distance
            if max_distance else 0
        )
        price_score = (
            charger["price_per_kwh"] / max_price
            if max_price else 0
        )
        return 0.6 * distance_score + 0.4 * price_score

    selected = min(chargers, key=score)

    selected_cost = next(
        (
            option["total_cost"]
            for option in cost["options"]
            if option["charger_id"] == selected["id"]
        ),
        None,
    )

    return {
        "agent": "Agent 4: Recommendation Agent",
        "selected": {
            **selected,
            "estimated_total_cost": selected_cost,
        },
        "urgency": emergency["urgency"],
        "message": (
            f"Recommended {selected['name']} "
            "based on demo distance and price."
        ),
    }


def frontend_recommendation(priority="balanced", budget=100):
    """
    Recommendation function for the new NXTWATT frontend.

    Uses the same Python charger dataset as the existing agents.
    The priority and budget are supplied by the frontend.
    """
    chargers = [
        charger.copy()
        for charger in DEMO_CHARGERS
        if charger.get("available", False)
        and charger.get("verified_installation", False)
        and charger["price_per_kwh"] <= budget
    ]

    def sort_key(charger):
        if priority == "price":
            return (
                charger["price_per_kwh"],
                charger["distance_km"],
            )

        if priority == "speed":
            return (
                -charger.get("power_kw", charger.get("kw", 0)),
                charger["price_per_kwh"],
            )

        if priority == "green":
            return (
                not charger.get("solar", False),
                charger["price_per_kwh"],
                charger["distance_km"],
            )

        if priority == "distance":
            return (
                charger["distance_km"],
                charger["price_per_kwh"],
            )

        # Balanced default: prioritize proximity and price.
        return (
            charger["distance_km"] * 0.6
            + charger["price_per_kwh"] * 0.4,
            charger["distance_km"],
        )

    chargers.sort(key=sort_key)

    if not chargers:
        return {
            "success": True,
            "recommendation": None,
            "message": (
                "No available verified demo chargers match "
                "your budget. Try increasing it."
            ),
        }

    selected = chargers[0]

    return {
        "success": True,
        "recommendation": {
            **selected,
            "estimated_total_cost": round(
                selected["price_per_kwh"] * 10, 2
            ),
        },
        "message": (
            "Recommendation calculated from the demo dataset. "
            "The estimated total assumes 10 kWh."
        ),
    }


def run_workflow(battery, range_km, energy_kwh, connector):
    agent1 = emergency_analyzer(
        battery, range_km, energy_kwh
    )

    agent2 = home_charger_finder(
        range_km, connector, energy_kwh
    )

    agent3 = cost_benefit_advisor(
        energy_kwh, agent2["matches"]
    )

    agent4 = recommendation_agent(
        agent1, agent2, agent3
    )

    gemma_explanation = gemma_explanation_agent(
        recommendation=agent4,
        battery=battery,
        range_km=range_km,
        energy_kwh=energy_kwh,
        eligible_chargers=agent2["matches"],
        cost_options=agent3["options"],
    )

    return {
        "success": True,
        "agents": [agent1, agent2, agent3, agent4],
        "recommendation": agent4,
        "gemma_explanation": gemma_explanation,
    }


def gemma_explanation_agent(
    recommendation,
    battery,
    range_km,
    energy_kwh,
    eligible_chargers,
    cost_options,
):
    import json
    import requests

    selected = recommendation.get("selected")

    if not selected:
        return (
            "No suitable demo charger matches your requirements. "
            "Try another connector or a smaller energy request. "
            "All listings are simulated demo data."
        )

    chargers = []

    for charger in eligible_chargers:
        matching_cost = next(
            (
                option["total_cost"]
                for option in cost_options
                if option["charger_id"] == charger["id"]
            ),
            None,
        )

        chargers.append({
            "name": charger["name"],
            "distance_km": charger["distance_km"],
            "price_per_kwh": charger["price_per_kwh"],
            "connectors": charger["connectors"],
            "estimated_total_cost": matching_cost,
        })

    if not chargers:
        return (
            "No eligible chargers are available for comparison. "
            "All listings are simulated demo data."
        )

    cheapest = min(
        chargers,
        key=lambda charger: charger["estimated_total_cost"],
    )
    closest = min(
        chargers,
        key=lambda charger: charger["distance_km"],
    )

    facts = (
        f"Cheapest: {cheapest['name']}, "
        f"Rs. {cheapest['estimated_total_cost']} total. "
        f"Closest: {closest['name']}, "
        f"{closest['distance_km']} km away. "
        f"Selected: {selected['name']}."
    )

    prompt = f"""
You are the explanation agent for NXTWATT.

Battery: {battery}%
Remaining range: {range_km} km
Requested energy: {energy_kwh} kWh

Python-calculated facts:
{facts}

Selected recommendation:
{json.dumps(selected, indent=2)}

Charger comparison:
{json.dumps(chargers, indent=2)}

Explain the recommendation in 3 short sentences.
Use the supplied facts exactly. Never invent prices, distances,
routes, traffic or live availability. Do not call a charger
the cheapest unless the supplied data proves it.
State that the listings are simulated demo data.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=60,
        )
        response.raise_for_status()

        answer = response.json().get("response", "").strip()
        if answer:
            return answer

        return (
            "Gemma returned no explanation. "
            "Use the Python-calculated recommendation and costs."
        )

    except requests.RequestException:
        return (
            "Gemma is unavailable. Use the Python-calculated "
            "recommendation and cost estimates. "
            "All listings are simulated demo data."
        )
