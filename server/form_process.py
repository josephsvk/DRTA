import uuid

@app.post("/process-form-data")
async def process_form_data(file: UploadFile = File(...)):
    """Process form_data.json content and perform various tasks."""
    print("Processing form_data.json.")
    file_content = await file.read()
    data = json.loads(file_content.decode('utf-8'))  # Parse JSON content

    # Retrieve environment variables
    env_prefix = os.getenv("IPV6_PREFIX", "default_prefix")
    port_range_start = int(os.getenv("PORT_RANGE_START", "8000"))
    port_range_end = int(os.getenv("PORT_RANGE_END", "9000"))
    used_ports = set()  # Set to keep track of used ports

    # Extract values from the uploaded file
    device_name = data.get("device_name")
    ipv6_prefix = data.get("ipv6_prefix")
    location = data.get("location")
    function = data.get("function")

    # Validate IPv6 prefix
    if ipv6_prefix != env_prefix:
        return {"error": "Invalid IPv6 prefix. Process terminated."}

    # Generate a new unique port
    for port in range(port_range_start, port_range_end):
        if port not in used_ports:
            used_ports.add(port)
            break
    else:
        return {"error": "No available ports in the defined range."}

    # Generate a unique identifier
    unique_id = str(uuid.uuid4())

    # Create a response object
    response_data = {
        "device_name": device_name,
        "file_name": f"{device_name}_data.json",
        "ipv6_prefix": ipv6_prefix,
        "port": port,
        "location": location,
        "function": function,
        "unique_id": unique_id
    }

    # Log the processed data
    print(f"Processed data: {response_data}")

    # Return the processed data to the client
    return response_data
