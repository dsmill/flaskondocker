import subprocess
import time
import multiprocessing


def register_account(username, password, base_url):
    register_start_time = time.time_ns()

    # Prepare registration command
    email_address = f"{username}@test.com"
    register_command = [
        "curl", "-X", "POST", f"{base_url}/register",
        "-d", f"username={username}",
        "-d", f"email={email_address}",
        "-d", f"password={password}",
        "-d", f"password2={password}"
    ]

    # Execute registration request
    subprocess.run(register_command)
    register_end_time = time.time_ns()

    return register_end_time - register_start_time


def sign_in_account(username, password, base_url):
    signin_start_time = time.time_ns()

    # Prepare sign-in command
    signin_command = [
        "curl", "-X", "POST", f"{base_url}/login",
        "-d", f"username={username}",
        "-d", f"password={password}"
    ]

    # Execute sign-in request
    subprocess.run(signin_command)
    signin_end_time = time.time_ns()

    return signin_end_time - signin_start_time


def make_post(text_body, base_url):
    post_start_time = time.time_ns()

    # Prepare post command
    post_command = [
        "curl", "-X", "POST", f"{base_url}/post",
        "-d", f"post={text_body}"
    ]

    # Execute post request
    subprocess.run(post_command)
    post_end_time = time.time_ns()

    return post_end_time - post_start_time


def process_account(username, password, base_url, test_posts):
    account_start_time = time.time_ns()

    # Register account
    setup_time = 0
    register_time = register_account(username, password, base_url)
    
    # Sign in to the account
    signin_time = sign_in_account(username, password, base_url)

    # Make each test post
    post_times = []
    for post in test_posts:
        with open(f"webcrawler_tests/posts/{post}.txt", "r") as post_text_file:
            post_content = post_text_file.read()
            post_time = make_post(post_content, base_url)
            post_times.append(post_time)

    account_end_time = time.time_ns()
    total_time = account_end_time - account_start_time

    # Send timings back to the main process
    return {
        'username': username,
        'setup_time': setup_time,
        'register_time': register_time,
        'signin_time': signin_time,
        'post_times': post_times,
        'total_time': total_time
    }


timings_list = []

def log_result(result):
    timings_list.append(result)


if __name__ == "__main__":
    program_start_time = time.time_ns()

    base_url = "http://localhost:3000"
    test_posts = ["hello_world", "line_breaks", "special_characters", "max_characters"]
    usernames_file = open("webcrawler_tests/usernames_10.txt")

    # Read usernames from file
    usernames = [line.strip() for line in usernames_file if line.strip()]
    usernames_file.close()

    pool = multiprocessing.Pool(processes=3)

    for uname in usernames:
        # Get password, default to "password" if file is exhausted
        password = uname

        # Create a new process for each account
        pool.apply_async(process_account, args=(uname, password, base_url, test_posts), callback=log_result)

    # Wait for all processes to finish
    pool.close()
    pool.join()

    timing_file_name = "webcrawlerv3_3cores_time.txt"

    # Write timing information to file
    with open(timing_file_name, "a") as timing_file:
        for entry in timings_list:
            timing_data = entry
            timing_file.write(f"Setup Time: {timing_data['setup_time']}ns for Username: {timing_data['username']}\n")
            timing_file.write(f"Register Time: {timing_data['register_time']}ns for Username: {timing_data['username']}\n")
            timing_file.write(f"Sign_in Time: {timing_data['signin_time']}ns for Username: {timing_data['username']}\n")
            for i, post_time in enumerate(timing_data['post_times']):
                timing_file.write(f"Post Time: {post_time}ns for Username: {timing_data['username']}\n")
            timing_file.write(f"Total Time for Account {timing_data['username']}: {timing_data['total_time']}ns\n")

    program_end_time = time.time_ns()

    with open(timing_file_name, "a") as timing_file:
        timing_file.write(f"Total Program Time: {program_end_time - program_start_time}ns\n")
