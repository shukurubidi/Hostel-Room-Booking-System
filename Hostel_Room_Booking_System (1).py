import json
import os

DATA_FILE = "hostel_data.json"

# Hostel structure: 55 total spaces
ROOMS = {
    "Block A": {f"A{100 + i}": 4 for i in range(1, 6)},   # A101-A105
    "Block B": {f"B{200 + i}": 4 for i in range(1, 6)},   # B201-B205
    "Block C": {f"C{300 + i}": 3 for i in range(1, 6)},   # C301-C305
}


def default_data():
    return {
        "students": {},
        "rooms": {
            block: {room: [] for room in rooms}
            for block, rooms in ROOMS.items()
        }
    }


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return True
    except (OSError, TypeError) as error:
        print(f"Could not save data: {error}")
        return False


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Basic validation of the saved file
        if not isinstance(data, dict) or "students" not in data or "rooms" not in data:
            raise ValueError("Invalid data structure")

        return data

    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        print("Warning: The data file is missing or damaged.")
        print("The system will start with default records.")
        return default_data()


def get_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if value < 0:
                print("Value cannot be negative.")
            else:
                return value
        except ValueError:
            print("Please enter a valid number.")


def register_student(data):
    print("\n" + "=" * 45)
    print("STUDENT REGISTRATION")
    print("=" * 45)

    reg_no = get_non_empty("Enter registration number: ")

    if reg_no in data["students"]:
        print("A student with that registration number already exists.")
        return

    name = get_non_empty("Enter student name: ")
    course = get_non_empty("Enter course: ")
    year = get_non_empty("Enter year of study: ")
    phone = get_non_empty("Enter phone number: ")
    fee = get_positive_float("Enter total hostel fee: ")

    data["students"][reg_no] = {
        "registration_number": reg_no,
        "name": name,
        "course": course,
        "year_of_study": year,
        "phone": phone,
        "block": None,
        "room": None,
        "total_fee": fee,
        "total_paid": 0.0,
        "payments": []
    }

    save_data(data)

    print("\nSTUDENT REGISTERED SUCCESSFULLY!")
    print(f"Registration Number: {reg_no}")
    print(f"Name: {name}")
    print(f"Course: {course}")
    print(f"Year of Study: {year}")
    print(f"Phone: {phone}")
    print(f"Total Hostel Fee: {fee:,.2f}")
    print(f"Outstanding Balance: {fee:,.2f}")


def find_student(data, reg_no):
    return data["students"].get(reg_no)


def allocate_room(data):
    print("\n" + "=" * 45)
    print("ROOM ALLOCATION")
    print("=" * 45)

    reg_no = get_non_empty("Enter student registration number: ")
    student = find_student(data, reg_no)

    if student is None:
        print("Student not found.")
        return

    if student["room"] is not None:
        print(
            f"This student is already allocated to "
            f"{student['block']} - {student['room']}."
        )
        return

    print("\nAvailable rooms:")
    for block, rooms in ROOMS.items():
        print(f"\n{block}")
        for room, capacity in rooms.items():
            occupied = len(data["rooms"][block][room])
            available = capacity - occupied
            if available > 0:
                print(
                    f"{room}: Capacity {capacity} | "
                    f"Occupied {occupied} | Available {available}"
                )

    room_number = get_non_empty("\nEnter room number: ").upper()

    selected_block = None
    selected_capacity = None

    for block, rooms in ROOMS.items():
        if room_number in rooms:
            selected_block = block
            selected_capacity = rooms[room_number]
            break

    if selected_block is None:
        print("Invalid room number.")
        return

    occupied = len(data["rooms"][selected_block][room_number])

    if occupied >= selected_capacity:
        print("This room is full. Please choose another room.")
        return

    data["rooms"][selected_block][room_number].append(reg_no)
    student["block"] = selected_block
    student["room"] = room_number

    save_data(data)

    print("\nROOM ALLOCATION SUCCESSFUL!")
    print(f"Student: {student['name']}")
    print(f"Registration Number: {reg_no}")
    print(f"Block: {selected_block}")
    print(f"Room: {room_number}")
    print(f"Remaining spaces: {selected_capacity - occupied - 1}")


def record_fee_payment(data):
    print("\n" + "=" * 45)
    print("FEE PAYMENT")
    print("=" * 45)

    reg_no = get_non_empty("Enter student registration number: ")
    student = find_student(data, reg_no)

    if student is None:
        print("Student not found.")
        return

    balance = student["total_fee"] - student["total_paid"]

    if balance <= 0:
        print("This student has already fully paid.")
        return

    print(f"Student: {student['name']}")
    print(f"Outstanding balance: {balance:,.2f}")

    amount = get_positive_float("Enter payment amount: ")

    if amount <= 0:
        print("Payment must be greater than zero.")
        return

    if amount > balance:
        print("Payment cannot be greater than the outstanding balance.")
        return

    student["total_paid"] += amount
    student["payments"].append(amount)

    balance = student["total_fee"] - student["total_paid"]

    save_data(data)

    status = "FULLY PAID" if balance == 0 else "OUTSTANDING"

    print("\nPAYMENT RECORDED SUCCESSFULLY!")
    print(f"Payment Made: {amount:,.2f}")
    print(f"Total Paid: {student['total_paid']:,.2f}")
    print(f"Outstanding Balance: {balance:,.2f}")
    print(f"Payment Status: {status}")


def search_student(data):
    print("\n" + "=" * 45)
    print("SEARCH STUDENT")
    print("=" * 45)

    search = get_non_empty(
        "Enter student name or registration number: "
    ).lower()

    found = []

    for student in data["students"].values():
        if (
            search in student["name"].lower()
            or search in student["registration_number"].lower()
        ):
            found.append(student)

    if not found:
        print("No student found.")
        return

    print("\nSTUDENT SEARCH RESULTS")

    for student in found:
        balance = student["total_fee"] - student["total_paid"]
        status = "FULLY PAID" if balance == 0 else "OUTSTANDING"

        print("\n" + "-" * 45)
        print(f"Registration Number: {student['registration_number']}")
        print(f"Name: {student['name']}")
        print(f"Course: {student['course']}")
        print(f"Year of Study: {student['year_of_study']}")
        print(f"Phone: {student['phone']}")
        print(f"Hostel Block: {student['block'] or 'Not allocated'}")
        print(f"Room: {student['room'] or 'Not allocated'}")
        print(f"Total Hostel Fee: {student['total_fee']:,.2f}")
        print(f"Total Paid: {student['total_paid']:,.2f}")
        print(f"Outstanding Balance: {balance:,.2f}")
        print(f"Payment Status: {status}")


def full_occupancy_report(data):
    print("\n" + "=" * 60)
    print("FULL OCCUPANCY REPORT")
    print("=" * 60)

    total_capacity = 0
    total_occupied = 0

    for block, rooms in ROOMS.items():
        block_occupied = 0
        block_capacity = sum(rooms.values())

        print(f"\n{block}")

        for room, capacity in rooms.items():
            students_in_room = data["rooms"][block][room]
            occupied = len(students_in_room)
            available = capacity - occupied

            total_capacity += capacity
            total_occupied += occupied
            block_occupied += occupied

            print(
                f"\nRoom: {room}\n"
                f"Capacity: {capacity} | "
                f"Occupied: {occupied} | "
                f"Available: {available}"
            )

            if students_in_room:
                print("Students:")
                for reg_no in students_in_room:
                    student = data["students"].get(reg_no)
                    if student:
                        print(
                            f"- {student['name']} "
                            f"({student['registration_number']})"
                        )
            else:
                print("Students: None")

        print(
            f"\n{block} SUMMARY: "
            f"Occupied = {block_occupied}, "
            f"Capacity = {block_capacity}, "
            f"Available = {block_capacity - block_occupied}"
        )

    print("\n" + "-" * 45)
    print("OVERALL HOSTEL SUMMARY")
    print("-" * 45)
    print(f"Total Capacity: {total_capacity}")
    print(f"Total Occupied: {total_occupied}")
    print(f"Total Available: {total_capacity - total_occupied}")


def fee_defaulters(data):
    print("\n" + "=" * 45)
    print("FEE DEFAULTERS")
    print("=" * 45)

    threshold = get_positive_float(
        "Enter minimum outstanding balance threshold: "
    )

    found = False

    for student in data["students"].values():
        balance = student["total_fee"] - student["total_paid"]

        if balance > threshold:
            found = True
            print(
                f"\n{student['name']} "
                f"({student['registration_number']})"
            )
            print(f"Outstanding Balance: {balance:,.2f}")

    if not found:
        print("No fee defaulters found above that threshold.")


def view_all_students(data):
    print("\n" + "=" * 45)
    print("ALL STUDENTS")
    print("=" * 45)

    if not data["students"]:
        print("No students registered.")
        return

    for student in data["students"].values():
        balance = student["total_fee"] - student["total_paid"]
        print(
            f"\n{student['registration_number']} | "
            f"{student['name']} | "
            f"{student['course']} | "
            f"Balance: {balance:,.2f}"
        )


def main_menu():
    print("\n" + "=" * 50)
    print("HOSTEL ROOM BOOKING AND FEES MANAGEMENT SYSTEM")
    print("=" * 50)
    print("1. Register Student")
    print("2. Allocate Room")
    print("3. Record Fee Payment")
    print("4. Search Student")
    print("5. View Full Occupancy Report")
    print("6. View Fee Defaulters")
    print("7. View All Students")
    print("8. Save Data")
    print("9. Exit")


def main():
    data = load_data()

    while True:
        main_menu()
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            register_student(data)

        elif choice == "2":
            allocate_room(data)

        elif choice == "3":
            record_fee_payment(data)

        elif choice == "4":
            search_student(data)

        elif choice == "5":
            full_occupancy_report(data)

        elif choice == "6":
            fee_defaulters(data)

        elif choice == "7":
            view_all_students(data)

        elif choice == "8":
            if save_data(data):
                print("Data saved successfully.")

        elif choice == "9":
            print("\nSaving data before exit...")
            if save_data(data):
                print("Data saved successfully.")
            print("Goodbye!")
            break

        else:
            print("Invalid menu choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
