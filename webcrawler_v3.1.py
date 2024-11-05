from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import multiprocessing

def create_chrome_driver(username: str, url: str):
    setup_start_time = time.time_ns()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    print(driver.title)

    setup_end_time = time.time_ns()

    return driver, setup_end_time - setup_start_time

def register_account(driver, username: str, password: str):
    register_start_time = time.time_ns()

    register_button = driver.find_element(By.LINK_TEXT, "Click to Register!")
    register_button.click()

    print(driver.current_url)

    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(username)

    email_address = username + "@test.com"
    print(email_address)
    email_field = driver.find_element(By.ID, "email")
    email_field.send_keys(email_address)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    password2_field = driver.find_element(By.ID, "password2")
    password2_field.send_keys(password)

    submit_button = driver.find_element(By.ID, "submit")
    submit_button.click()

    register_end_time = time.time_ns()

    return register_end_time - register_start_time

def sign_in_account(driver, username: str, password: str):
    signin_start_time = time.time_ns()

    print(driver.title)
    print(driver.current_url)

    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(username)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    submit_button = driver.find_element(By.ID, "submit")
    submit_button.click()

    signin_end_time = time.time_ns()

    return signin_end_time - signin_start_time

def make_post(driver, text_body: str, username: str):
    post_start_time = time.time_ns()

    post_field = driver.find_element(By.ID, "post")
    post_field.send_keys(text_body)

    submit_button = driver.find_element(By.ID, "submit")
    submit_button.click()

    post_end_time = time.time_ns()

    return post_end_time - post_start_time

def close_driver(driver):
    driver.close()

timings_list = []
def log_result(result):
    timings_list.append(result)

def process_account(username: str, password: str, url: str, test_posts: list):
    account_start_time = time.time_ns()

    # Create and initialize driver
    driver, setup_time = create_chrome_driver(username, url)
    register_time = register_account(driver, username, password)
    signin_time = sign_in_account(driver, username, password)

    # Make each test post
    post_times = []
    for post in test_posts:
        post_text_file = open(f"webcrawler_tests/posts/{post}.txt", "r")
        post_content = post_text_file.read()
        post_time = make_post(driver, post_content, username)
        post_times.append(post_time)

    # Close the driver
    close_driver(driver)

    account_end_time = time.time_ns()
    total_time = account_end_time - account_start_time

    # Send timings back to the main process
    return ({
        'username': username,
        'setup_time': setup_time,
        'register_time': register_time,
        'signin_time': signin_time,
        'post_times': post_times,
        'total_time': total_time
    })

if __name__ == "__main__":
    program_start_time = time.time_ns()

    url = "http://localhost:3000/"
    test_posts = ["hello_world", "line_breaks", "special_characters", "max_characters"]
    usernames_file = open("webcrawler_tests/usernames_10.txt")
    passwords_file = open("webcrawler_tests/passwords.txt")

    # Create a Queue to collect timing information
    processes = []
    active_processes = []
    usernames = []
    u = usernames_file.readline().strip()
    while len(u) > 0:
        usernames.append(u)
        u = usernames_file.readline().strip()

    pool = multiprocessing.Pool(processes=3)

    for uname in usernames:
        # Get password, default to "password" if file is exhausted
        password = uname

        # Create a new process for each account
        pool.apply_async(process_account, args=(uname, password, url, test_posts), callback=log_result)

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

    usernames_file.close()
    passwords_file.close()
