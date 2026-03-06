using System;
using System.Collections.Generic;

namespace JASON_Compiler
{
    static class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=====================================");
            Console.WriteLine("   JASON COMPILER - Mac Debug Mode   ");
            Console.WriteLine("=====================================");

            // Example JASON code to test
            string testCode = "IF x = 5 THEN WRITE x";

            Console.WriteLine($"\nScanning code: {testCode}");

            Scanner scanner = new Scanner();
            scanner.StartScanning(testCode);

            // Display results from the List inside the scanner
            Console.WriteLine("\n--- Resulting Tokens ---");
            if (scanner.Tokens.Count == 0)
            {
                Console.WriteLine("No tokens found yet. (Make sure your IF statements in Scanner.cs are implemented!)");
            }
            else
            {
                foreach (var token in scanner.Tokens)
                {
                    Console.WriteLine($"Lexeme: {token.lex} | Type: {token.token_type}");
                }
            }

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}