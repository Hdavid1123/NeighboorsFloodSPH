from Config.utils.create_ics import create_ics_txt

def generate_ics(boundary_json, fluid_json, txt_path, log_path):
    ret = create_ics_txt(
        boundary_path=str(boundary_json),
        fluid_path=str(fluid_json),
        output_path=str(txt_path),
        output_log_path=str(log_path)
    )
    return ret == 0
