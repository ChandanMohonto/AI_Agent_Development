from state import (
    create_state,
    add_action,
    record_observation,
    next_step,
    can_continue,
    finish
)


async def run_agent_loop(
    user_request,
    planner,
    execute_action,
    format_answer,
    tools,
    client
):

    state = create_state(user_request)

    # The heart of our agent
    while can_continue(state):

        # 1. THINK - the planner decides the next action
        action = planner(state, tools)

        print("Planner Selected:", action)

        if action == "FINISH":

            answer = format_answer(state)

            finish(state, answer)

            break

        # Guard: don't run the same tool twice
        if action in state["actions"]:

            print("  -> already done, skipped")

            record_observation(
                state,
                action,
                "Skipped: already done. Choose a different tool or FINISH."
            )

            next_step(state)

            continue

        # 2. ACT - execute the action via MCP
        try:

            observation = await execute_action(
                action,
                client
            )

        except Exception as error:

            observation = f"Error: {error}"

        # 3. OBSERVE - remember what happened
        add_action(
            state,
            action
        )

        record_observation(
            state,
            action,
            observation
        )

        next_step(state)

    # Safety net: max_steps reached without FINISH
    if not state["finished"]:

        print("Max steps reached - writing answer from results so far.")

        finish(state, format_answer(state))

    return state