-- SELECT CategoryID, MIN(UnitsInStock)
-- FROM Products
-- GROUP BY CategoryID
-- HAVING MIN(UnitsInStock) < 10

-- SELECT Title, COUNT(*) as NEmp
-- FROM Employees
-- GROUP BY Title
-- HAVING COUNT(*) > 4

-- INSERT into Employees (LastName, FirstName, HireDate, City) VALUES('King', 'Anne', '1998-01-01', 'London')
-- INSERT into Employees (LastName, FirstName, HireDate, City) VALUES('Loaura', 'Anne', '1998-01-10', 'Seattle')

-- SELECT *
-- FROM Employees


-- UPDATE Employees SET HireDate = '1998-10-10' WHERE EmployeeID = 5

-- DELETE From Employees WHERE EmployeeID = 10

-- CREATE PROCEDURE Retrieve
--     @CustomerID NCHAR
-- AS
-- BEGIN

-- SELECT *
-- FROM Orders
-- WHERE CustomerID = @CustomerID

-- END;

-- DECLARE @CxID = ''
-- EXEC Retrieve @CustomerID = @CxID

-- CREATE PROCEDURE Sales
--     @PID INT,
--     @Tot INT OUTPUT
-- AS

-- BEGIN

-- SELECT SUM(Quantity*UnitPrice)
-- FROM [Order Details]
-- WHERE ProductID = @PID

-- END;

-- DECLARE @ProdID = ''
-- EXEC Sales @PID = @CxID

-- CREATE FUNCTION fn.GetOrdersByYear (@OrderDate YEAR)
-- RETURNS TABLE
-- AS
-- RETURN 
-- (
--     SELECT *
--     FROM Orders
--     WHERE YEAR(OrderDate) = @OrderDate
-- );

-- CREATE FUNCTION fn_GetProductsByPriceRange (@RangeType NVARCHAR(MAX))
-- RETURNS @ReturnT TABLE (Pid INT, Pname NVARCHAR(MAX), Uprice MONEY)
-- AS
-- BEGIN
--     IF @RangeType = 'Budget'
--     BEGIN
--         INSERT INTO @ReturnT
--         SELECT ProductID, ProductName, UnitPrice
--         FROM Products
--         WHERE UnitPrice < 20
--     END
--     ELSE IF @RangeType = 'Premium'
--     BEGIN
--         INSERT INTO @ReturnT
--         SELECT ProductID, ProductName, UnitPrice
--         FROM Products
--         WHERE UnitPrice >= 20
--     END 

--     RETURN;
-- END

-- SELECT *
-- FROM fn.GetOrdersByYear(1997)