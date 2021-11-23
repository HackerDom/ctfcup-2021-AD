namespace CtfLand.Service.Models
{
    public record OperationResult
    {
        public bool IsSuccess { get; protected set; }

        public static OperationResult CreateFailed()
        {
            return new OperationResult { IsSuccess = false };
        }

        public static OperationResult CreateSuccess()
        {
            return new OperationResult { IsSuccess = true };
        }
    }

    public record OperationResult<T> : OperationResult
    {
        public T Result { get; private set; }

        public new static OperationResult<T> CreateFailed()
        {
            return new OperationResult<T> { IsSuccess = false };
        }

        public static OperationResult<T> CreateSuccess(T result)
        {
            return new OperationResult<T> { IsSuccess = true, Result = result };
        }
    }
}