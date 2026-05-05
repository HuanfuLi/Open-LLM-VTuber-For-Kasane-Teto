# Roadmap: Vivid Actions

## Phase 1: Core Backend Implementation
- [ ] Task 1.1: Expand `Actions` dataclass to include `motions: Optional[List[str]]`.
- [ ] Task 1.2: Update `Live2dModel` to handle `motionMap` and provide `extract_motion`.
- [ ] Task 1.3: Update `actions_extractor` decorator to extract both expressions and motions.
- [ ] Task 1.4: Update `Live2dModel.remove_emotion_keywords` (or rename to `remove_action_tags`) to clean both expressions and motions.

## Phase 2: Configuration & Prompts
- [ ] Task 2.1: Update `model_dict.json` with sample `motionMap` for existing models.
- [ ] Task 2.2: Update `prompts/utils/live2d_expression_prompt.txt` to include motion instructions.
- [ ] Task 2.3: Ensure `Live2dModel.emo_str` (or a new `action_str`) includes motions for the prompt.

## Phase 3: Validation & Refinement
- [ ] Task 3.1: Create a test script or unit tests for motion extraction.
- [ ] Task 3.2: Verify the combined extraction of expressions and motions.
- [ ] Task 3.3: (Optional) Verify frontend receives the payload correctly using logs.
