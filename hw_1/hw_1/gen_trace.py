
def generate_pipeline():
    # Instructions for n=5
    # 1. mov x4, x0
    # 2. cmp w1, 0
    # 3. ble .L4 (Not taken)
    # 4. mov x2, 0
    # 5. mov w0, 0
    # -- Loop 1 --
    # 6. ldr w3, [x4, x2, lsl 2]
    # 7. add w0, w0, w3
    # 8. add x2, x2, 1
    # 9. cmp w1, w2
    # 10. bgt .L3 (Taken)
    # -- Loop 2 --
    # 11-15
    # -- Loop 3 --
    # 16-20
    # -- Loop 4 --
    # 21-25
    # -- Loop 5 --
    # 26-30
    # -- End --
    # 31. ret

    instructions = [
        "mov x4, x0", "cmp w1, 0", "ble .L4", "mov x2, 0", "mov w0, 0",
        "ldr w3, [ptr]", "add w0, w0, w3", "add x2, x2, 1", "cmp w1, w2", "bgt .L3",
        "ldr w3, [ptr]", "add w0, w0, w3", "add x2, x2, 1", "cmp w1, w2", "bgt .L3",
        "ldr w3, [ptr]", "add w0, w0, w3", "add x2, x2, 1", "cmp w1, w2", "bgt .L3",
        "ldr w3, [ptr]", "add w0, w0, w3", "add x2, x2, 1", "cmp w1, w2", "bgt .L3",
        "ldr w3, [ptr]", "add w0, w0, w3", "add x2, x2, 1", "cmp w1, w2", "bgt .L3",
        "ret"
    ]
    
    types = [
        "ALU", "ALU", "BR", "ALU", "ALU",
        "LD", "ALU", "ALU", "ALU", "BR",
        "LD", "ALU", "ALU", "ALU", "BR",
        "LD", "ALU", "ALU", "ALU", "BR",
        "LD", "ALU", "ALU", "ALU", "BR",
        "LD", "ALU", "ALU", "ALU", "BR",
        "BR"
    ]
    
    # Simplified deps for the trace
    # (instr_idx, reg_produced)
    producers = {} # reg -> (instr_idx, time_available)
    
    num_instr = len(instructions)
    stages = [{} for _ in range(num_instr)]
    
    # State
    fetch_ptr = 0
    decode_ptr = 0
    iq = [] # list of indices
    iq_capacity = 2
    issue_ptr = 0
    
    # Hardware status
    mem_units = [0] * 5 # time until free
    
    # Results available (instr_idx -> cycle)
    available_at = {}

    for cycle in range(1, 150):
        # 1. WB / Finish
        for i in range(num_instr):
            if cycle in stages[i].values():
                pass # just checking
        
        # 2. Issue (from IQ to E1)
        issued_this_cycle = 0
        while issued_this_cycle < 2 and iq:
            idx = iq[0]
            instr_type = types[idx]
            
            # Check RAW
            can_issue = True
            # Manual dependency check based on the assembly logic
            if idx == 2: # ble depends on flags from instr 1 (cmp)
                if 1 not in available_at or cycle < available_at[1]: can_issue = False
            if idx == 6: # ldr Iter 1 depends on x4 (instr 0) and x2 (instr 3)
                if 0 not in available_at or cycle < available_at[0]: can_issue = False
                if 3 not in available_at or cycle < available_at[3]: can_issue = False
            if idx == 7: # add depends on w3 (instr 5) and w0 (instr 4 or previous add)
                if 5 not in available_at or cycle < available_at[5]: can_issue = False
                # ... and so on.
            
            # For simplicity in this script, let's just model the key ones
            # ALU: depends on previous if used.
            # In our loop:
            # add w0, w0, w3 -> depends on w3 (LD) and w0 (prev ALU)
            # add x2, x2, 1 -> depends on x2 (prev ALU)
            # cmp w1, w2 -> depends on x2 (prev ALU)
            # bgt -> depends on cmp (prev ALU)
            
            # Simplified Logic:
            def get_dep(idx):
                if idx == 0: return []
                if idx == 1: return []
                if idx == 2: return [1] # ble -> cmp
                if idx == 3: return []
                if idx == 4: return []
                # Loop start (6, 7, 8, 9, 10)
                if idx % 5 == 1 and idx >= 6: # ldr (6, 11, 16...) depends on x4(0) and x2(prev iteration add)
                    return [0, idx-3]
                if idx % 5 == 2: # add (7, 12...) depends on ldr(idx-1) and w0(idx-5 or 4)
                    return [idx-1, idx-5 if idx > 7 else 4]
                if idx % 5 == 3: # add x2 (8, 13...) depends on x2(idx-5 or 3)
                    return [idx-5 if idx > 8 else 3]
                if idx % 5 == 4: # cmp (9, 14...) depends on x2(idx-1)
                    return [idx-1]
                if idx % 5 == 0 and idx >= 10: # bgt (10, 15...) depends on cmp(idx-1)
                    return [idx-1]
                if idx == 31: # ret
                    return [idx-1]
                return []

            deps = get_dep(idx)
            for d in deps:
                if d not in available_at or cycle < available_at[d]:
                    can_issue = False
                    break
            
            if not can_issue:
                break # Head stalls, rest stalls
            
            # Issue it
            stages[idx]['E1'] = cycle
            iq.pop(0)
            issued_this_cycle += 1
            
            # Calculate completion and availability
            if instr_type == "ALU":
                stages[idx]['E2'] = cycle + 1
                stages[idx]['WB'] = cycle + 2
                available_at[idx] = cycle + 1 # after E2
            elif instr_type == "LD":
                stages[idx]['M1'] = cycle + 1
                stages[idx]['M2'] = cycle + 2
                stages[idx]['M3'] = cycle + 3
                stages[idx]['WB'] = cycle + 4
                available_at[idx] = cycle + 3 # after M3
            elif instr_type == "BR":
                # BRANCH: F -> D -> E1 (3 cycles total)
                available_at[idx] = cycle # result ready immediately? "Исполнение инструкций перехода занимает 1 такт."
                # Stage is just E1.
        
        # 3. Decode -> IQ
        # Instructions decoded in previous cycle enter IQ if space
        # But wait: "Декодирование ... занимают 1 такт."
        # Instructions in D at T-1 enter IQ at T.
        to_iq = []
        for i in range(num_instr):
            if stages[i].get('D') == cycle - 1:
                to_iq.append(i)
        
        for idx in to_iq:
            if len(iq) < iq_capacity:
                iq.append(idx)
                # Success
            else:
                # IQ Full. This instruction stays in D?
                # "If IQ is full, Fetch/Decode stop".
                # So this instruction stays in D, and fetch_ptr doesn't advance.
                # Let's adjust decode_ptr.
                pass

        # 4. Fetch / Decode
        # (This logic is a bit complex for a quick script, let's just emit the table for report)
    
    # Actually, I'll just write the final table by hand after thinking it through, 
    # it's more reliable than a half-baked script for a 30-instr trace.

generate_pipeline()
