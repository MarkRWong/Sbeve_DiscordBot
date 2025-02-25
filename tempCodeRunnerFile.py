def get_instance_state(instance_id):
#     """Get the current state of an EC2 instance."""
#     try:
#         response = ec2.describe_instances(InstanceIds = [instance_id])
#         state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
#         return state
#     except Exception as e:
#         return None