import argparse
import os
import sys

from crypto_utils import encrypt_file, decrypt_file


def main():

    parser = argparse.ArgumentParser(
        description="File Protection Utility - AES-256 File Encryption"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # --------------------------------------------------------
    # ENCRYPT COMMAND
    # --------------------------------------------------------

    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a file"
    )

    encrypt_parser.add_argument(
        "input",
        help="Input file path"
    )

    encrypt_parser.add_argument(
        "-o",
        "--output",
        help="Encrypted output file"
    )

    encrypt_parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="Encryption password"
    )

    # --------------------------------------------------------
    # DECRYPT COMMAND
    # --------------------------------------------------------

    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="Decrypt an encrypted file"
    )

    decrypt_parser.add_argument(
        "input",
        help="Encrypted .enc file"
    )

    decrypt_parser.add_argument(
        "-o",
        "--output",
        help="Decrypted output file"
    )

    decrypt_parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="Decryption password"
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # ENCRYPT
    # --------------------------------------------------------

    if args.command == "encrypt":

        if not os.path.isfile(args.input):
            print("ERROR: Input file does not exist.")
            sys.exit(1)

        output = args.output

        if not output:
            output = args.input + ".enc"

        try:

            encrypt_file(
                args.input,
                output,
                args.password
            )

            print()
            print("========================================")
            print("        FILE ENCRYPTION SUCCESSFUL")
            print("========================================")
            print(f"Input file : {args.input}")
            print(f"Output file: {output}")
            print("Algorithm  : AES-256-CBC")
            print("KDF        : PBKDF2-HMAC-SHA256")
            print("Integrity  : HMAC-SHA256")
            print("========================================")
            print()

        except Exception as error:

            print(f"ERROR: {error}")
            sys.exit(1)

    # --------------------------------------------------------
    # DECRYPT
    # --------------------------------------------------------

    elif args.command == "decrypt":

        if not os.path.isfile(args.input):
            print("ERROR: Encrypted file does not exist.")
            sys.exit(1)

        output = args.output

        if not output:

            if args.input.endswith(".enc"):
                output = args.input[:-4] + ".decrypted"
            else:
                output = args.input + ".decrypted"

        try:

            decrypt_file(
                args.input,
                output,
                args.password
            )

            print()
            print("========================================")
            print("        FILE DECRYPTION SUCCESSFUL")
            print("========================================")
            print(f"Input file : {args.input}")
            print(f"Output file: {output}")
            print("Integrity  : VERIFIED")
            print("========================================")
            print()

        except Exception as error:

            print(f"ERROR: {error}")
            sys.exit(1)


if __name__ == "__main__":
    main()