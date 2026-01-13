from app.miro_client import test_connection, create_class_box

BOARD_ID = "uXjVGRZh1IE="

print("Testing Miro connection...")
print(test_connection())

print("Creating rectangle...")
create_class_box(
    BOARD_ID,
    "Customer",
    ["customerIdnamenamenamenamenamenamen", "name", "name", "name", "name", "name", "name", "name", "name", "name"],
    x=0,
    y=0
)
print("Done.")


