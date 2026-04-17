#include <iostream>
#include <ctime>
#include <cstdlib>
#include <vector>

using namespace std;

void getMaxSubarraySum(vector<int> &arr, vector<int> &subArray)
{
    int maxSum = arr[0];
    int size = 0;
    for (int i = 0; i < arr.size(); i++)
    {
        int sum = arr[i];
        for (int j = i; j < arr.size(); j++)
        {
            sum += arr[j];
        }
        if (sum > maxSum)
        {
            maxSum = sum;
            subArray.clear();
            for (int k = 0; k < arr.size() - i; k++)
            {
                subArray.push_back(arr[i + k]);
            }
        }
    }
    cout << "Original Array: ";
    printArray(arr);
    cout << "Maximum Subarray: ";
    printArray(subArray);
    cout << "Maximum Subarray Sum: " << maxSum << endl;
}

vector<int> getMaxSubarray(const vector<int> &arr)
{
    vector<int> subArray; // Create a vector for the subarray
    getMaxSubarraySum(const_cast<vector<int> &>(arr), subArray);
    return subArray;
}

vector<int> generateRandomArray()
{
    vector<int> arr(rand() % 100); // Random size between 0 and 99
    for (int i = 0; i < arr.size(); i++)
    {
        int magnitude = rand() % 100;
        bool isPositive = (rand() % 2 == 0);
        arr[i] = isPositive ? magnitude : -magnitude; // Random numbers between 0 and 99 positive and negative
    }
    return arr;
}

void printArray(const vector<int> &arr)
{
    for (int num : arr)
    {
        cout << num << " ";
    }
    cout << endl;
}

void findPairswithSum(const vector<int> &arr, int targetSum)
{
    cout << "Pairs with sum " << targetSum << ": ";
    for (int i = 0; i < arr.size(); i++)
    {
        for (int j = i + 1; j < arr.size(); j++)
        {
            if (arr[i] + arr[j] == targetSum)
            {
                cout << "(" << arr[i] << ", " << arr[j] << ") ";
            }
        }
    }
    cout << endl;
}

int main()
{
    srand(time(0)); // Seed the random number generator
    vector<int> result = getMaxSubarray(generateRandomArray());
    // The result is printed inside the getMaxSubarraySum function
    return 0;
}