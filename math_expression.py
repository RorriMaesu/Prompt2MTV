import math

class ComfyMathExpression:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "expression": ("STRING", {"multiline": False, "default": "a/2"}),
            },
            "optional": {
                "values.a": ("*", {"forceInput": True}),
                "values.b": ("*", {"forceInput": True}),
                "values.c": ("*", {"forceInput": True}),
                "values.d": ("*", {"forceInput": True}),
                "values.e": ("*", {"forceInput": True}),
                "values.f": ("*", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("FLOAT", "INT", "BOOLEAN")
    FUNCTION = "evaluate"
    CATEGORY = "math"

    def evaluate(self, expression, **kwargs):
        eval_ctx = {}
        for key, val in kwargs.items():
            if key.startswith("values."):
                var_name = key.split(".", 1)[1] # e.g. "a"
                if val is not None:
                    try:
                        # Convert string numbers to float/int if needed
                        if isinstance(val, str):
                            if "." in val:
                                val = float(val)
                            else:
                                val = int(val)
                    except ValueError:
                        pass
                    eval_ctx[var_name] = val

        # Provide defaults for a-f if not defined
        for c in "abcdef":
            if c not in eval_ctx:
                eval_ctx[c] = 0

        # Provide standard math functions
        eval_ctx.update({
            "math": math,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "ceil": math.ceil,
            "floor": math.floor,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "int": int,
            "float": float,
        })

        try:
            # Evaluate using eval
            res = eval(expression, {"__builtins__": {}}, eval_ctx)
        except Exception as e:
            print(f"[MathExpression Error] Failed to evaluate expression '{expression}' with ctx {eval_ctx}: {e}")
            res = 0

        try:
            val_int = int(res)
        except (ValueError, TypeError):
            val_int = 0

        try:
            val_float = float(res)
        except (ValueError, TypeError):
            val_float = 0.0

        val_bool = bool(res)

        return (val_float, val_int, val_bool)

NODE_CLASS_MAPPINGS = {
    "ComfyMathExpression": ComfyMathExpression
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyMathExpression": "Math Expression"
}
