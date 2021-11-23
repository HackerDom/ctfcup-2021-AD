using System;
using System.Threading;
using System.Threading.Tasks;
using CtfLand.Service.Models;

namespace CtfLand.Service.Providers
{
    public static class TaskRunner
    {
        public static async Task<OperationResult> RunWithTimeout(Func<Task> func, TimeSpan timeout)
        {
            var cts = new CancellationTokenSource();

            var funcTask = Task.Run(func, cts.Token);
            var task = await Task.WhenAny(
                    Task.Delay(timeout),
                    funcTask)
                .ConfigureAwait(false);

            if (task == funcTask)
                return OperationResult.CreateSuccess();

            cts.Cancel();
            return OperationResult.CreateFailed();
        }
    }
}