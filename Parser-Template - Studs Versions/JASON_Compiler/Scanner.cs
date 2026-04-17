using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

public enum Token_Class
{
/*    Begin, Call, Declare, End, Do, Else, EndIf, EndUntil, EndWhile, If, Integer,
    Parameters, Procedure, Program, Read, Real, Set, Then, Until, While, Write,
    Dot, Semicolon, Comma, LParanthesis, RParanthesis, EqualOp, LessThanOp,
    GreaterThanOp, NotEqualOp, PlusOp, MinusOp, MultiplyOp, DivideOp,
    Idenifier, Constant, OrOp, AndOp, Comment
    */

    Repeat, Int, Float, String, End, Else, ElseIf, If, Read, Write, Return,
    Then, Until, Program, Semicolon, Comma, LParanthesis, RParanthesis, 
    LCurly, RCurly, EqualOp, LessThanOp, GreaterThanOp, NotEqualOp, PlusOp, MinusOp,
    MultiplyOp, DivideOp, AssignOp, OrOp, AndOp, Idenifier, Constant, Comment, Dot

}
namespace JASON_Compiler
{
    

    public class Token
    {
       public string lex;
       public Token_Class token_type;
    }


    public class Scanner
    {
        public List<Token> Tokens = new List<Token>();
        Dictionary<string, Token_Class> ReservedWords = new Dictionary<string, Token_Class>();
        Dictionary<string, Token_Class> Operators = new Dictionary<string, Token_Class>();

        public Scanner()
        {
/*            ReservedWords.Add("if", Token_Class.If);
            ReservedWords.Add("begin", Token_Class.Begin);
            ReservedWords.Add("call", Token_Class.Call);
            ReservedWords.Add("declare", Token_Class.Declare);
            ReservedWords.Add("end", Token_Class.End);
            ReservedWords.Add("do", Token_Class.Do);
            ReservedWords.Add("else", Token_Class.Else);
            ReservedWords.Add("endif", Token_Class.EndIf);
            ReservedWords.Add("enduntil", Token_Class.EndUntil);
            ReservedWords.Add("endwhile", Token_Class.EndWhile);
            ReservedWords.Add("integer", Token_Class.Integer);
            ReservedWords.Add("parameters", Token_Class.Parameters);
            ReservedWords.Add("procedure", Token_Class.Procedure);
            ReservedWords.Add("program", Token_Class.Program);
            ReservedWords.Add("read", Token_Class.Read);
            ReservedWords.Add("real", Token_Class.Real);
            ReservedWords.Add("set", Token_Class.Set);
            ReservedWords.Add("then", Token_Class.Then);
            ReservedWords.Add("until", Token_Class.Until);
            ReservedWords.Add("while", Token_Class.While);
            ReservedWords.Add("write", Token_Class.Write); */

            ReservedWords.Add("int", Token_Class.Int);       
            ReservedWords.Add("float", Token_Class.Float);
            ReservedWords.Add("string", Token_Class.String);
            ReservedWords.Add("read", Token_Class.Read);
            ReservedWords.Add("write", Token_Class.Write);
            ReservedWords.Add("repeat", Token_Class.Repeat);      
            ReservedWords.Add("until", Token_Class.Until);
            ReservedWords.Add("if", Token_Class.If);
            ReservedWords.Add("elseif", Token_Class.ElseIf);       
            ReservedWords.Add("else", Token_Class.Else);
            ReservedWords.Add("then", Token_Class.Then);
            ReservedWords.Add("return", Token_Class.Return);        
            ReservedWords.Add("endl", Token_Class.Write);
            ReservedWords.Add("main", Token_Class.Program);
            ReservedWords.Add("end", Token_Class.End);

            //Operators.Add(".", Token_Class.Dot);
            Operators.Add(";", Token_Class.Semicolon);
            Operators.Add(",", Token_Class.Comma);
            Operators.Add("(", Token_Class.LParanthesis);
            Operators.Add(")", Token_Class.RParanthesis);
            Operators.Add("{", Token_Class.LCurly);
            Operators.Add("}", Token_Class.RCurly);
            Operators.Add("=", Token_Class.EqualOp);
            Operators.Add("<", Token_Class.LessThanOp);
            Operators.Add(">", Token_Class.GreaterThanOp);
            //Operators.Add("!", Token_Class.NotEqualOp);
            Operators.Add("+", Token_Class.PlusOp);
            Operators.Add("-", Token_Class.MinusOp);
            Operators.Add("*", Token_Class.MultiplyOp);
            Operators.Add("/", Token_Class.DivideOp);
            Operators.Add(":=", Token_Class.AssignOp);          
            Operators.Add("<>", Token_Class.NotEqualOp);   
            Operators.Add("&&", Token_Class.AndOp);      
            Operators.Add("||", Token_Class.OrOp);         
                     

        }

    public void StartScanning(string SourceCode)
        {
            for(int i=0; i<SourceCode.Length;i++)
            {
                int j = i;
                char CurrentChar = SourceCode[i];
                string CurrentLexeme = CurrentChar.ToString();

                if (CurrentChar == ' ' || CurrentChar == '\r' || CurrentChar == '\n' || CurrentChar == '\t')
                    continue;

                //identifiers & keywords
                if (char.IsLetter(CurrentChar))
                {
                    j = i + 1;
                    while (j < SourceCode.Length && (char.IsLetterOrDigit(SourceCode[j])))
                    {
                        CurrentLexeme += SourceCode[j];
                        j++;
                    }
                    FindTokenClass(CurrentLexeme);
                    i = j - 1;
                }

                //numbers
                else if(char.IsDigit(CurrentChar))
                {
                    j = i + 1;
                    while (j < SourceCode.Length && (char.IsDigit(SourceCode[j]) || SourceCode[j] == '.'))
                    {
                        CurrentLexeme += SourceCode[j];
                        j++;
                    }
                    FindTokenClass(CurrentLexeme);
                    i = j - 1;
                }

                //strings
                else if (CurrentChar == '"')
                {
                    j = i + 1;
                    while (j < SourceCode.Length && SourceCode[j] != '"')
                    {
                        CurrentLexeme += SourceCode[j];
                        j++;
                    }
                    if (j < SourceCode.Length)
                    {
                        CurrentLexeme += '"';
                        i = j;
                    }
                    FindTokenClass(CurrentLexeme);
                }

                //else if (CurrentChar == '{')
                //{
                //    j++;
                //    CurrentChar = SourceCode[j];
                //    while (CurrentChar != '}')
                //    {
                //        j++;
                //        CurrentChar = SourceCode[j];
                //    }
                //    i = j;
                //}


                // //comments
                // else if (CurrentChar == '/' && i + 1 < SourceCode.Length && SourceCode[i + 1] == '*')
                // {
                //     CurrentLexeme = "/*";
                //     j = i + 2;
                //     while (j + 1 < SourceCode.Length && !(SourceCode[j] == '*' && SourceCode[j + 1] == '/'))
                //     {
                //         CurrentLexeme += SourceCode[j];
                //         j++;
                //     }
                //     if (j + 1 < SourceCode.Length)
                //     {
                //         CurrentLexeme += "*/";
                //         FindTokenClass(CurrentLexeme);
                //         i = j + 1;
                //     }
                // }

                //operators
                else
                {
                    if (i + 1 < SourceCode.Length)
                    {
                        if (CurrentChar == ':' && SourceCode[i + 1] == '=')
                        {
                            CurrentLexeme = ":=";
                            i++;
                        }
                        else if (CurrentChar == '<' && SourceCode[i + 1] == '>')
                        {
                            CurrentLexeme = "<>";
                            i++;
                        }
                        else if (CurrentChar == '&' && SourceCode[i + 1] == '&')
                        {
                            CurrentLexeme = "&&";
                            i++;
                        }
                        else if (CurrentChar == '|' && SourceCode[i + 1] == '|')
                        {
                            CurrentLexeme = "||";
                            i++;
                        }
                    }
                    FindTokenClass(CurrentLexeme);
                }
            }
            
            JASON_Compiler.TokenStream = Tokens;
        }
        void FindTokenClass(string Lex)
        {
            Token_Class TC;
            Token Tok = new Token();
            Tok.lex = Lex;

            if (ReservedWords.ContainsKey(Lex))
            {
                TC = ReservedWords[Lex];
                Tok.token_type = TC;
                Tokens.Add(Tok);
            }

            else if (Operators.ContainsKey(Lex))
            {
                TC = Operators[Lex];
                Tok.token_type = TC;
                Tokens.Add(Tok);
            }

            else if (isIdentifier(Lex))
            {
                TC = Token_Class.Idenifier;
                Tok.token_type = TC;
                Tokens.Add(Tok);
            }

            else if (isConstant(Lex))
            {
                TC = Token_Class.Constant;
                Tok.token_type = TC;
                Tokens.Add(Tok);
            }

            else if (Lex.StartsWith("\"") && Lex.EndsWith("\""))
            {
                TC = Token_Class.String;
                Tok.token_type = TC;
                Tokens.Add(Tok);
            }   
            
            // else if (Lex.StartsWith("/*") && Lex.EndsWith("*/"))
            // {
            //     TC = Token_Class.Comment;
            //     Tok.token_type = TC;
            //     Tokens.Add(Tok);
            // }
            else
            {
                Errors.Error_List.Add("Unidentified Token "+ Lex );
            }


        }

    

        bool isIdentifier(string lex)
        {
            bool isValid=true;
            if (string.IsNullOrEmpty(lex) || !char.IsLetter(lex[0]))
            { isValid = false; }

            else
            {
                for (int i = 1; i < lex.Length; i++)
                {
                    if(!char.IsLetterOrDigit(lex[i]))
                    {
                        isValid = false;
                    }
                }
            }
            return isValid;
        }
        bool isConstant(string lex)
        {
            bool isValid = true;
            if (string.IsNullOrEmpty(lex))
            {
                isValid = false;
            }

            int dotCount = 0;
            for (int i = 0; i < lex.Length; i++)
            {
                if (lex[i] == '.')
                {
                    dotCount++;
                    if (dotCount > 1)
                        isValid = false;
                }
                else if (!char.IsDigit(lex[i]))
                {
                    isValid = false;
                }
            }
            return isValid;
        }
    }
}
