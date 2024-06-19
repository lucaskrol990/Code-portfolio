'''
This function translates a referees id (potential list) to the corresponding index in the referee_df
'''

def referee_id_to_idx(referee_id, gs):
    if not isinstance(referee_id, list): # Not a list, i.e. singular value
        tmp_list = referee_id == gs['referee_df']['id']
        unconverted_ref_ids = []
        referee_idx = []
        if sum(tmp_list) == 1:
            referee_idx.append(tmp_list.tolist().index(True))
        else:
            # print(f"Id {referee_id} has no associated index, set to {gs['nrefs'] - 1}")
            unconverted_ref_ids.append(referee_id)
            referee_idx = gs['nrefs'] - 1
        # referee_idx = tmp_list.tolist().index(True)
        return referee_idx, unconverted_ref_ids
    else:
        referee_idx = []
        unconverted_ref_ids = []
        for id in referee_id:
            tmp_list = id == gs['referee_df']['id']
            if sum(tmp_list) == 1:
                referee_idx.append(tmp_list.tolist().index(True))
            else:
                # print(f"Id {id} has no associated index, set to {gs['nrefs'] - 1}")
                unconverted_ref_ids.append(id)
                referee_idx.append(gs['nrefs'] - 1)
        return referee_idx, unconverted_ref_ids