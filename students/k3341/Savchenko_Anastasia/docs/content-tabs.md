## Content Tabs

This is some examples of content tabs.

### Generic Content

=== "Plain text"

    This is some plain text

=== "Unordered list"

    * First item
    * Second item
    * Third item

=== "Ordered list"

    1. First item
    2. Second item
    3. Third item

=== "Next one"

    This is some plain text

### New headind

Some plaiin text. Huge text.

### New headind 2

=== "Nothing"

=== "Code 1"

    ```py title="tcp_client.py" linenums="1" hl_lines="3-4"
    import socket
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((socket.gethostname(), 1234))
    
    client.send('Hello, server'.encode('utf-8'))
    print(client.recv(1024).decode('utf-8'))
    client.send('Bye, server'.encode('utf-8'))
    print(client.recv(1024).decode('utf-8'))
    ```

=== "Nothing"


### Code Blocks in Content Tabs

=== "Python"

    ```py
    def main():
        print("Hello world!")

    if __name__ == "__main__":
        main()
    ```

=== "JavaScript"

    ```js
    function main() {
        console.log("Hello world!");
    }

    main();
    ```